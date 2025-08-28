from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel
import os
import json
import logging
# Note: avoid importing get_database_session at module import time to keep
# this module lightweight for dev-server imports. Import the DB dependency
# inside functions if needed. Also avoid importing optional heavy deps at
# module import time.

# Import auth dependency lazily with a safe fallback so this module can be
# imported in lightweight dev contexts where SQLAlchemy or other heavy
# modules may not be importable. If the real `get_current_user` cannot be
# imported, expose a dev stub that acts as an admin user (only for dev).
try:
    # Prefer absolute import so the module can be loaded by filepath via importlib
    # without triggering "relative import with no known parent package" errors.
    from backend.api.auth import get_current_user
except Exception:
    try:
        from ..api.auth import get_current_user
    except Exception as _err:
        # Only use the dev fallback when explicitly running in development mode.
        # This prevents silently weakening auth in production-like environments.
        if os.getenv("ENVIRONMENT", "").lower() == "development":
            logging.warning("⚠️ admin_settings: falling back to dev stub for get_current_user due to import error: %s", _err)

            class _DevAdminUser:
                user_type = 'admin'
                is_active = True
                username = 'dev_admin'

            def get_current_user():
                return _DevAdminUser()
        else:
            # Re-raise so imports fail loudly outside development.
            raise

router = APIRouter(prefix="/admin", tags=["admin"])

SECRETS_PATH = os.path.join(os.path.dirname(__file__), '..', '.secrets.json')


class ApiKeyPayload(BaseModel):
    provider: str
    api_key: str
    notes: str = ""


class MeliTokenRequest(BaseModel):
    provider: str = 'mercadolibre'
    client_id: str | None = None
    client_secret: str | None = None



def _load_secrets() -> Dict[str, Any]:
    try:
        if os.path.exists(SECRETS_PATH):
            with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        return {}
    return {}


def _save_secrets(data: Dict[str, Any]):
    # Ensure parent dir exists
    parent = os.path.dirname(SECRETS_PATH)
    os.makedirs(parent, exist_ok=True)
    with open(SECRETS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def _require_admin(user=Depends(get_current_user)):
    # Simple admin check based on user_type; enforce admin-only access
    if getattr(user, 'user_type', None) != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.get('/settings')
def get_settings(current_user=Depends(_require_admin)):
    """Return stored API keys (masked) and integrations metadata"""
    secrets = _load_secrets()
    masked = {}
    for k, v in secrets.items():
        api_key = v.get('api_key') if isinstance(v, dict) else None
        if api_key:
            masked[k] = {
                'api_key_masked': api_key[:4] + '...' + api_key[-4:],
                'notes': v.get('notes', '')
            }
        else:
            masked[k] = v
    return {'success': True, 'settings': masked}


@router.post('/settings')
def set_setting(payload: ApiKeyPayload, current_user=Depends(_require_admin)):
    """Store/update an API key for a provider. Secrets are stored server-side in a gitignored file."""
    secrets = _load_secrets()
    secrets[payload.provider] = {
        'api_key': payload.api_key,
        'notes': payload.notes,
    }
    _save_secrets(secrets)
    return {'success': True, 'message': f"Stored key for {payload.provider}"}


@router.delete('/settings/{provider}')
def delete_setting(provider: str, current_user=Depends(_require_admin)):
    secrets = _load_secrets()
    if provider in secrets:
        del secrets[provider]
        _save_secrets(secrets)
        return {'success': True, 'message': f"Deleted {provider}"}
    raise HTTPException(status_code=404, detail='Provider not found')


@router.post('/meli/token')
def exchange_mercadolibre_token(payload: MeliTokenRequest, current_user=Depends(_require_admin)):
    """Exchange client credentials for a Mercado Libre access token.

    If client_id/client_secret are provided in the request they are used.
    Otherwise the endpoint will look for stored credentials in the admin secrets under `provider`.
    Stored credentials may be either an access token (stored as `api_key`) or a dict with
    `client_id` and `client_secret` fields.
    """
    # Determine credentials
    client_id = payload.client_id
    client_secret = payload.client_secret

    if not client_id or not client_secret:
        secrets = _load_secrets()
        if payload.provider not in secrets:
            raise HTTPException(status_code=400, detail="No credentials found for provider and none supplied")
        stored = secrets[payload.provider]
        # If stored is a dict with client_id/client_secret use them
        if isinstance(stored, dict) and 'client_id' in stored and 'client_secret' in stored:
            client_id = client_id or stored['client_id']
            client_secret = client_secret or stored['client_secret']
        # If stored contains an api_key assume it's already an access token
        elif isinstance(stored, dict) and 'api_key' in stored:
            return {
                'success': True,
                'access_token': stored['api_key'],
                'note': 'Returned stored api_key as access_token'
            }
        else:
            raise HTTPException(status_code=400, detail="Stored credentials format not recognized")

    # Call Mercado Libre token endpoint
    token_url = 'https://api.mercadolibre.com/oauth/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    # Import requests lazily to avoid import-time side-effects
    try:
        import requests
    except Exception as _err:
        raise HTTPException(status_code=500, detail=f"Missing dependency 'requests': {_err}")

    try:
        resp = requests.post(token_url, data=data, headers={'Accept': 'application/json'}, timeout=15)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Request to Mercado Libre failed: {e}")

    if resp.status_code != 200:
        # Relay Mercado Libre response for debugging
        raise HTTPException(status_code=502, detail={
            'status': resp.status_code,
            'body': resp.text
        })

    return resp.json()

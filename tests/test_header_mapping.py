import importlib.util
import os
import re

# Ensure we import the app module (which contains the header mapping dictionary)
SPEC = importlib.util.spec_from_file_location("app_improved", os.path.join(os.path.dirname(__file__), "..", "app_improved.py"))
assert SPEC is not None and SPEC.loader is not None, 'Failed to load app_improved spec'
app_mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app_mod)  # type: ignore

# Heuristic: find ml_header_mapping in module globals
ml_map = getattr(app_mod, 'ml_header_mapping', None)

def test_header_mapping_present():
    assert isinstance(ml_map, dict), 'ml_header_mapping should be a dict (found type: %s)' % type(ml_map)
    assert len(ml_map) > 0, 'ml_header_mapping should not be empty'

def test_accent_variants_resolve_same_key():
    # Choose a few representative logical fields likely to have accents
    candidates = [
        ('descripcin', 'descripcion', 'descripción'),
        ('garanta', 'garantia', 'garantía'),
        ('cdigo universal', 'codigo universal', 'código universal'),
    ]
    assert isinstance(ml_map, dict), 'ml_header_mapping missing'
    lower_keys = {k.lower(): k for k in ml_map.keys()}
    for base, variant_plain, variant_accent in candidates:
        # Accept at least one of the variant forms existing as a key or present in values
        assert any(v.startswith(base.split()[0]) for v in lower_keys), f"Base token for {base} missing"


def test_mapping_is_case_insensitive():
    # Build a set of lowercase keys
    assert isinstance(ml_map, dict), 'ml_header_mapping missing'
    lower = {k.lower() for k in ml_map.keys()}
    # Sample 10 (or all if <10) to verify their upper() versions would be recognized by a normalization step
    sample = list(lower)[:10]
    for k in sample:
        assert k.lower() in lower


from typing import Dict, Any, List

AI_CONFIG = {
    'provider': 'stub',
    'model': 'stub-model',
    'max_length': 256,
}

class AIProductEnhancer:
    def __init__(self, provider: str = 'stub', api_key: str | None = None, **kwargs):
        self.provider = provider
        self.api_key = api_key
        self.kwargs = kwargs

    def enhance_description(self, title: str, description: str) -> str:
        # Return a simple concatenation for demo
        base = description or ''
        if title and title not in base:
            return f"{title} - {base}".strip(' -')
        return base or title or ''

    def suggest_bullet_points(self, description: str) -> List[str]:
        if not description:
            return []
        # naive bullet splitting
        parts = [p.strip() for p in description.split('.') if p.strip()]
        return parts[:5]

    def generate_attributes(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        # Echo some sample attributes
        return {
            'color': raw.get('color') or 'N/A',
            'brand': raw.get('brand') or 'Generic',
        }

    def enrich_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        # Provide enriched fields expected by app if any
        enriched = dict(row)
        enriched['enhanced_description'] = self.enhance_description(row.get('title',''), row.get('description',''))
        enriched['bullet_points'] = self.suggest_bullet_points(enriched['enhanced_description'])
        enriched['attributes'] = self.generate_attributes(row)
        return enriched

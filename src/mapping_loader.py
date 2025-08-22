import yaml

def load_mapping(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config["template_columns"], config["mapping"]


def resolve_column_aliases(product_columns, mapping):
    """Resolve mapping values against actual product columns.

    Args:
      product_columns: iterable of column names from the product DataFrame
      mapping: dict of ml_label -> product_field (may be alias)

    Returns:
      dict of ml_label -> resolved_product_column_or_None
    """
    import difflib, unicodedata

    def normalize_text(s):
        if s is None:
            return ''
        if not isinstance(s, str):
            s = str(s)
        s = s.lower().strip()
        s = unicodedata.normalize('NFKD', s)
        s = ''.join(ch for ch in s if not unicodedata.combining(ch))
        return s

    product_cols = list(product_columns)
    norm_product_cols = {normalize_text(c): c for c in product_cols}

    alias_keywords = {
        'title': ['titulo', 'título', 'title', 'nombre', 'nombre_producto', 'name'],
        'price': ['precio', 'price', 'cost', 'valor', 'costo'],
        'stock': ['stock', 'cantidad', 'qty', 'quantity'],
        'category': ['categoria', 'categoría', 'category', 'tipo'],
        'condition': ['condicion', 'condición', 'condition'],
        'sku': ['sku', 'reference', 'codigo', 'código'],
        'images': ['imagen', 'image', 'images', 'fotos', 'foto']
    }

    def resolve_mapping_value(val):
        if val is None:
            return None
        if val in product_cols:
            return val
        nval = normalize_text(val)
        # if the normalized value matches any alias keyword, use that keyword set
        for alias_key, kws in alias_keywords.items():
            if any(nval == normalize_text(kw) for kw in kws):
                for pc in product_cols:
                    npc = normalize_text(pc)
                    if any(kw in npc for kw in kws):
                        return pc
        if nval in norm_product_cols:
            return norm_product_cols[nval]
        for npc, orig in norm_product_cols.items():
            if nval in npc or npc in nval:
                return orig
        try:
            matches = difflib.get_close_matches(nval, list(norm_product_cols.keys()), n=1, cutoff=0.7)
            if matches:
                return norm_product_cols[matches[0]]
        except Exception:
            pass
        return None

    resolved = {}
    for ml_field, product_field in mapping.items():
        r = None
        try:
            if isinstance(product_field, str) and product_field in product_cols:
                r = product_field
            else:
                r = resolve_mapping_value(product_field)
                if r is None:
                    r = resolve_mapping_value(ml_field)
        except Exception:
            r = None
        resolved[ml_field] = r

    return resolved
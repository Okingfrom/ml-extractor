from src.mapping_loader import resolve_column_aliases


def run_checks():
    # exact match
    cols = ['Nombre', 'Precio', 'Stock', 'Descripcion']
    mapping = {'Título': 'Nombre', 'Precio': 'Precio'}
    resolved = resolve_column_aliases(cols, mapping)
    assert resolved['Título'] == 'Nombre', f"expected 'Nombre', got {resolved['Título']}"
    assert resolved['Precio'] == 'Precio', f"expected 'Precio', got {resolved['Precio']}"

    # alias match
    cols = ['Nombre', 'Precio', 'Stock', 'Descripcion']
    mapping = {'Título': 'title', 'Precio': 'price'}
    resolved = resolve_column_aliases(cols, mapping)
    assert resolved['Título'] == 'Nombre', f"expected 'Nombre', got {resolved['Título']}"
    assert resolved['Precio'] == 'Precio', f"expected 'Precio', got {resolved['Precio']}"

    # fuzzy match
    cols = ['nombre_producto', 'precio_total', 'cantidad_disponible']
    mapping = {'Título': 'titulo', 'Precio': 'precio'}
    resolved = resolve_column_aliases(cols, mapping)
    assert resolved['Título'] == 'nombre_producto', f"expected 'nombre_producto', got {resolved['Título']}"
    assert resolved['Precio'] == 'precio_total', f"expected 'precio_total', got {resolved['Precio']}"

    print('All mapping resolution checks passed')


if __name__ == '__main__':
    run_checks()

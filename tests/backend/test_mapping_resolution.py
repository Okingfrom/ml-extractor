import pandas as pd
from src.mapping_loader import resolve_column_aliases


def test_exact_match():
    cols = ['Nombre', 'Precio', 'Stock', 'Descripcion']
    mapping = {'Título': 'Nombre', 'Precio': 'Precio'}
    resolved = resolve_column_aliases(cols, mapping)
    assert resolved['Título'] == 'Nombre'
    assert resolved['Precio'] == 'Precio'


def test_alias_match():
    cols = ['Nombre', 'Precio', 'Stock', 'Descripcion']
    mapping = {'Título': 'title', 'Precio': 'price'}
    resolved = resolve_column_aliases(cols, mapping)
    assert resolved['Título'] == 'Nombre'
    assert resolved['Precio'] == 'Precio'


def test_fuzzy_match():
    cols = ['nombre_producto', 'precio_total', 'cantidad_disponible']
    mapping = {'Título': 'titulo', 'Precio': 'precio'}
    resolved = resolve_column_aliases(cols, mapping)
    assert resolved['Título'] == 'nombre_producto'
    assert resolved['Precio'] == 'precio_total'

from src.enrichment.weight import enhance_weight

def test_weight_from_text():
    rec = {"title": "Producto 2.5kg peso"}
    out = enhance_weight(rec.copy())
    assert out["weight"] == 2.5
    assert out["weight_unit"] == "kg"

def test_weight_preserved():
    rec = {"weight": 9.9, "weight_unit": "kg"}
    out = enhance_weight(rec.copy())
    assert out["weight"] == 9.9
    assert out["weight_unit"] == "kg"

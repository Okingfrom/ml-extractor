from src.enrichment.brand import enhance_brand

def test_brand_from_title():
    rec = {"title": "Sony Headphones"}
    out = enhance_brand(rec.copy())
    assert out["brand"] == "Sony"

def test_brand_preserved():
    rec = {"title": "Sony Headphones", "brand": "SONY"}
    out = enhance_brand(rec.copy())
    assert out["brand"] == "SONY"

def test_brand_no_change_empty():
    rec = {"title": ""}
    out = enhance_brand(rec.copy())
    # Should not add brand if none detected
    assert out == rec

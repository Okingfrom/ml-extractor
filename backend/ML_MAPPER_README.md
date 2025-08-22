ML Mapper: Validations and Mapping Flow

This project includes a backend validator for Mercado Libre bulk templates that verifies structure and content before generation.

Key features:
- Checks presence of required sheets: `Publicaciones` and `Variaciones`.
- Validates required columns (SKU, ID de Variación, Precio, Cantidad/Stock, etc.).
- Groups variations by `ID de Variación` and enforces SKU uniqueness rules per parent.
- Validates price format and integer quantities.
- Verifies image URLs (HTTP 200) and reports invalid URLs.
- Produces a structured validation report with `errors` and `warnings`.

Usage (backend):
1. From the `backend` folder, run the validator against a template:

```powershell
cd backend
python test_ml_mapper.py ..\samples\plantilla_ml_ejemplo.xlsx
```

2. The script prints a JSON report with `errors`, `warnings` and `info` fields.

Developer notes:
- The validator is implemented in `backend/services/ml_mapper.py` and exposes `MLMapperValidator`.
- Network calls to image URLs perform HEAD/GET requests with short timeouts; running the validator requires network access.
- If critical columns are missing, the validator stops and returns an error report. This protects the mapping from producing invalid output.

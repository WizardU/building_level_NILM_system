# OpenAPI contract

`NILM.json` is **generated**, not hand-written:

```bash
python scripts/export_openapi.py
```

It mirrors the FastAPI application (`backend/app`). The live, interactive
contract is always available at:

- http://127.0.0.1:8000/openapi.json
- http://127.0.0.1:8000/docs

Re-run the export script after changing routes or schemas, and commit the
result so reviewers can inspect the contract without starting the server.

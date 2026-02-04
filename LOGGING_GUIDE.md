# Logging & Seq Guide

## Logging Overview
- All logging is configured in `app/core/logger.py`. The `setup_logging` function builds a console handler and optionally wires in Seq when `SEQ_ENABLED` is `True`.
- Loggers created with `get_logger(__name__)` inherit this configuration, so every component (middleware, services, jobs, etc.) logs consistently.
- The middleware pipeline already uses structured logging: each exception emits a `.NET`-style multi-line message plus structured fields (`UserId`, `LogId`, `StatusCode`, `Path`, `ErrorInfo`, etc.) that Seq indexes when `support_extra_properties=True`.

## Seq Integration
1. Install Seq locally (recommended):
   ```bash
   docker run --name seq -d --restart unless-stopped -e ACCEPT_EULA=Y -p 5341:80 datalust/seq:latest
   ```
   or download from https://datalust.co/seq and run the Windows/Mac/Linux installer.
2. Update the active `.env` file (e.g., `.env.development`):
   ```env
   SEQ_ENABLED=True
   SEQ_SERVER_URL=http://localhost:5341
   SEQ_API_KEY=        # only if Seq requires it
   ```
3. Restart the FastAPI app so `setup_logging` is invoked with Seq parameters from `Settings`.
4. Access Seq UI at http://localhost:5341. The `support_extra_properties=True` flag ensures `extra` attributes such as `UserId`, `LogId`, `Type`, `StatusCode`, `Path`, `HttpMethod`, and nested `ErrorInfo` fields become searchable properties.

## Verifying Logging
- Trigger an error (e.g., hit a protected endpoint with an invalid token). You should see both the console output and a Seq entry that lists the structured fields under `Event properties`.
- Use Seq queries like:
  - `StatusCode == 500`
  - `Type == "UnauthorizedException"`
  - `LogId == "your-log-id"`
  - `Path == "/api/v1/roles/permissions"`
- The log title still uses the multi-line template for readability, but the structured properties are what Seq exposes in the UI (no `Extra_*` prefix anymore thanks to `StructuredLogger`).

## Troubleshooting
- If Seq lacks structured properties, verify:
  - `seqlog` is installed (`pip show seqlog`).
  - `SEQ_ENABLED` is `True` and the URL is reachable (e.g., `curl http://localhost:5341/api`).
  - `support_extra_properties=True` and `support_stack_info=True` are passed to `seqlog.log_to_seq` (already set).
- If console logs disappear, ensure the Seq handler was configured successfully; otherwise the console handler is added separately so logging continues.
- Adjust `LOG_LEVEL` (in `.env`) to `DEBUG` or `INFO` depending on how much noise you want in Seq.

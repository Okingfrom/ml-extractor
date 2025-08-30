Frontend deployment for extractorml.uy

Goal
- Build frontend (frontend/) for production and deploy the static files to ~/public_html/extractorml.uy/ so that the site root serves the SPA and API calls are proxied to Daphne on 127.0.0.1:8000.

Assumptions
- Node.js (>=16) and npm/yarn are available for building locally or on the server.
- Daphne is running at 127.0.0.1:8000 and serving API routes under /api/.
- You have SSH access to the server and permission to write into ~/public_html/extractorml.uy/.

Quick steps (summary)
1) From repo root or inside `frontend/` run:

```bash
cd frontend
npm ci
npm run build
```

2) Copy the `build/` (React) or `dist/` (Vue/Angular) output to the server public_html target (example below uses rsync):

```bash
# from local machine
rsync -avz frontend/build/ youruser@yourserver:/home/youruser/public_html/extractorml.uy/
```

3) Ensure `index.html` is at the root of `/home/youruser/public_html/extractorml.uy/` and static assets are present in their folders.
4) Place the `.htaccess` file (see `deploy/frontend.htaccess`) in `/home/youruser/public_html/extractorml.uy/.htaccess`.
5) Restart or confirm Daphne is running and reachable on 127.0.0.1:8000.

.htaccess (what it does)
- Serves existing static files directly.
- Proxies requests starting with `/api/` to Daphne (127.0.0.1:8000).
- Falls back to `index.html` for SPA routing.

.htaccess content (also included in repo at `deploy/frontend.htaccess`):
- RewriteCond %{REQUEST_FILENAME} -f
- RewriteRule ^ - [L]
- RewriteRule ^api/(.*)$ http://127.0.0.1:8000/api/$1 [P,L]
- RewriteRule ^ index.html [L]

Configure frontend environment
- Set API base URL in frontend env config (for example, in React `.env.production`):

```
REACT_APP_API_BASE_URL=https://extractorml.uy/api
```

Deploy script (optional)
- The repo contains `scripts/deploy_frontend.sh` which will build (locally) and rsync the built files to a configurable server target. Edit the variables at the top for your server user/host and target path.

Testing
- Visit https://extractorml.uy/
- Verify the SPA loads and that network calls to `/api/*` return 200 OK.
- Test a POST to `/api/auth/login` from the frontend UI.

Notes
- If the project uses another framework (Vue/Angular), adjust build folder name or npm build command accordingly.
- If you prefer CI/CD, you can wire the same steps into GitHub Actions to build and deploy on merge to main.

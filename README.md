# Todo app – CI/CD demo

FastAPI + Flask + SQLite todo app, managed with [uv](https://docs.astral.sh/uv/), shipped as a Docker image.

## Local

```bash
uv sync
uv run flask --app app.wsgi run --debug   # http://127.0.0.1:5000
uv run uvicorn app.asgi:app --reload     # http://127.0.0.1:8000
uv run pytest
uv run ruff check .
```

```bash
docker build -t todo-app . && docker run -p 8000:8000 -v todo-data:/data todo-app
```

## Pipelines

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | pull request | ruff, pytest, docker build (no push) |
| `release.yml` | push / merge to `main` | CI → auto semver tag + GitHub Release → push image to Docker Hub (`<version>` and `latest`) |
| `deploy.yml` | manual (`workflow_dispatch`) | Choose `dev`, `uat`, or `production`; deploy over SSH and run the matching checks |

The test layers intentionally differ by environment:

- **Development:** unit tests run in CI and use an in-process FastAPI client.
- **UAT:** E2E tests call the deployed service and exercise a todo lifecycle.
- **Production:** the deploy workflow runs a read-only health sanity test.

Create these values in each GitHub Environment used by `deploy.yml`:

- Secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`
- Variable: `DEPLOY_BASE_URL` for `uat` and `production`

Version bump: patch by default; include `#minor` or `#major` in a commit message to bump higher.

## Setup

Repo **variables**: `DOCKERHUB_USERNAME`
Repo **secrets**: `DOCKERHUB_TOKEN` (Docker Hub access token)
Environments `dev`, `uat`, and `production` (add required reviewers to `production` for approval) with secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`. Add `DEPLOY_BASE_URL` as a variable to `uat` and `production`.

The server needs Docker with the compose plugin and the SSH user in the `docker` group.
If the Docker Hub repo is private, run `docker login` once on the server.

Also enable Settings → Actions → General → Workflow permissions: *Read and write* (needed to push tags).

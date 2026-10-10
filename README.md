# Todo app – CI/CD demo

Flask + SQLite + plain HTML frontend, managed with [uv](https://docs.astral.sh/uv/), shipped as a Docker image.

## Local

```bash
uv sync
uv run flask --app app.wsgi run --debug   # http://127.0.0.1:5000
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
| `deploy.yml` | manual (`workflow_dispatch`) | SSH to the server, `docker compose pull && up -d` for the chosen version |

Version bump: patch by default; include `#minor` or `#major` in a commit message to bump higher.

## Setup

Repo **variables**: `DOCKERHUB_USERNAME`
Repo **secrets**: `DOCKERHUB_TOKEN` (Docker Hub access token)
Environment `production` (add required reviewers for approval) with secrets: `PROD_HOST`, `PROD_USER`, `PROD_SSH_KEY`

The server needs Docker with the compose plugin and the SSH user in the `docker` group.
If the Docker Hub repo is private, run `docker login` once on the server.

Also enable Settings → Actions → General → Workflow permissions: *Read and write* (needed to push tags).

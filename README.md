# mcp-test

Containerized MCP demo stack by **Vahid Tavakkoli (2026)**.

This project demonstrates how to orchestrate a local AI workflow with a Node.js backend, a static frontend, Python tool servers, SearxNG web search, and Ollama model inference using Docker Compose.

![MCP stack screenshot](./screenshot.png)

## Project overview

`mcp-test` is a practical reference setup for experimenting with tool-enabled LLM chat in a local environment. The backend receives user prompts, calls Ollama, executes requested tools (matrix inversion, Tower of Hanoi, internet search, time, weather), and returns a final response to the browser UI.

## Features

- Node.js backend API (`/api/chat`) with tool-call orchestration.
- Static frontend (Nginx) for interactive chat.
- Python MCP-style tool services:
  - Matrix inversion service
  - Hanoi solver service
- SearxNG integration for search results.
- Ollama integration for local model inference.
- Docker Compose orchestration for one-command startup.

## Architecture overview

```text
Browser UI (frontend:6180)
  -> Backend API (backend:6100, POST /api/chat)
     -> Ollama API (host.docker.internal:11434)
     -> MCP Matrix service (mcp-matrix:6101, POST /tool/matrix)
     -> MCP Hanoi service (mcp-hanoi:6102, POST /tool/hanoi)
     -> SearxNG (searxng:8080)
```

## Repository structure

```text
mcp-test/
├── backend/                # Node.js API and tool execution logic
├── frontend/               # Static HTML/JS UI served by Nginx
├── mcp-hanoi/              # Python FastAPI Hanoi tool server
├── mcp-matrix/             # Python FastAPI matrix tool server
├── searxng/config/         # SearxNG runtime config
├── docker-compose.yml      # Multi-service orchestration
└── README.md
```

## Prerequisites

- Docker + Docker Compose
- Ollama running on the host machine
- A pulled Ollama model (default in compose: `ministral-3:3b`)

### Ollama dependency notes

- The backend expects Ollama at `http://host.docker.internal:11434`.
- On Linux, if `host.docker.internal` is not available by default, configure host-gateway support for Docker.
- Make sure your selected model is pulled before chat requests.

### SearxNG dependency notes

- SearxNG is included as a containerized dependency in this stack.
- Backend searches route through `SEARXNG_URL=http://searxng:8080`.
- Public internet access from your Docker environment is required for meaningful search results.

## Setup and run

1. Clone:

   ```bash
   git clone https://github.com/vtavakkoli/mcp-test.git
   cd mcp-test
   ```

2. (Optional) create local env file:

   ```bash
   cp .env.example .env
   ```

3. Start services:

   ```bash
   docker compose up --build
   ```

4. Open the frontend:

   - `http://localhost:6180`

## Service endpoints (verified against `docker-compose.yml`)

| Service      | URL / Endpoint                          | Host Port |
|--------------|------------------------------------------|-----------|
| Frontend     | `http://localhost:6180`                  | 6180      |
| Backend      | `http://localhost:6100/api/chat`         | 6100      |
| MCP Matrix   | `http://localhost:6101/tool/matrix`      | 6101      |
| MCP Hanoi    | `http://localhost:6102/tool/hanoi`       | 6102      |
| SearxNG      | `http://localhost:6103`                  | 6103      |

## Example usage

### Chat request to backend

```bash
curl -X POST http://localhost:6100/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Invert matrix [[4,7],[2,6]]"}'
```

### Direct matrix tool request

```bash
curl -X POST http://localhost:6101/tool/matrix \
  -H "Content-Type: application/json" \
  -d '{"matrix":[[4,7],[2,6]]}'
```

### Direct Hanoi tool request

```bash
curl -X POST http://localhost:6102/tool/hanoi \
  -H "Content-Type: application/json" \
  -d '{"n":3}'
```

## Troubleshooting

- **Frontend loads but replies fail**
  - Confirm backend is running on `6100` and CORS is enabled.
- **Backend returns Ollama error**
  - Verify Ollama is running on host port `11434` and the configured model exists.
- **Search tool returns empty/failed results**
  - Check SearxNG container status and outbound network availability.
- **Matrix tool returns 400**
  - Ensure input is square and invertible.
- **Hanoi tool returns 400**
  - Ensure `n >= 1`.

## License

Licensed under the MIT License. See [LICENSE](./LICENSE).

---
Written by Vahid Tavakkoli, 2026.

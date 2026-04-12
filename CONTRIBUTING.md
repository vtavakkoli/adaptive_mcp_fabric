# Contributing

Thanks for your interest in contributing to **mcp-test**.

## Development principles

- Keep the current architecture intact (Node.js backend, static frontend, Python MCP servers, SearxNG, Docker Compose).
- Favor small, reviewable pull requests.
- Avoid breaking changes unless discussed in an issue first.

## Getting started

1. Fork the repository and create a branch from `main`.
2. Build and run locally:

   ```bash
   docker compose up --build
   ```

3. Verify the stack:
   - Frontend: `http://localhost:6180`
   - Backend health path in use: `POST /api/chat` on `http://localhost:6100`

## Pull request checklist

- [ ] I verified the stack still starts with Docker Compose.
- [ ] I kept behavior and service wiring compatible.
- [ ] I updated docs for any user-facing change.
- [ ] I used clear commit messages.

## Reporting issues

Please use the issue templates to provide reproduction steps, expected behavior, and logs where possible.

---
Written by Vahid Tavakkoli, 2026

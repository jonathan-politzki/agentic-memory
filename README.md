# Jean Memory Agent Integration

This repository documents the correct method for integrating AI agents with the Jean Memory service.

## Connection Method

The official and only supported method for connecting a compatible agent (e.g., the Claude desktop app) to your Jean Memory is by using the `npx install-mcp` command. This command configures your local agent environment to securely communicate with the Jean Memory server.

**Note:** Direct connections from custom scripts (e.g., via Python's `requests` or `mcp` libraries) are not supported and will be rejected by the server.

### Your Personalized Install Command

Run the following command in your terminal. It is unique to your user account and will install and configure the necessary client.

```bash
npx install-mcp https://api.jeanmemory.com/mcp/claude/sse/66d3d5d1-fc48-44a7-bbc0-1efa2e164fad --client claude
```

Once the command completes, your compatible agent will be connected to Jean Memory and will have access to all of its memory tools.

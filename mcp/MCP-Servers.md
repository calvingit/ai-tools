# MCP Servers Configuration Guide

This document provides an overview of all Model Context Protocol (MCP) servers configured in this environment, with information sourced from the official [MCP servers repository](https://github.com/modelcontextprotocol/servers).

---

## Table of Contents

1. [Installation Methods](#installation-methods)
2. [Browser Automation](#browser-automation)
3. [Documentation & Code Search](#documentation--code-search)
4. [Language-Specific Tools](#language-specific-tools)
5. [File System & Git Operations](#file-system--git-operations)
6. [Web Access](#web-access)
7. [Advanced Reasoning](#advanced-reasoning)
8. [Memory & Knowledge](#memory--knowledge)
9. [Time & Utilities](#time--utilities)
10. [Zhipu AI Services](#zhipu-ai-services)

---

## Installation Methods

### Claude Code CLI (Recommended)

Use the `claude mcp add` command to install MCP servers:

```bash
claude mcp add <server-name> -- <command>
```

Example:

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
```

### Manual Configuration

Alternatively, manually edit your `claude.json` configuration file with the server details.

---

## Browser Automation

### chrome-devtools

**Purpose**: Chrome browser automation and DevTools integration. Enables web page interaction, screenshot capture, network request inspection, and performance analysis.

**Official Documentation**: [chrome-devtools-mcp](https://github.com/ModelCloud/chrome-devtools-mcp)

**Claude Code CLI Installation**:

```bash
claude mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
```

---

## Documentation & Code Search

### context7

**Purpose**: Retrieves up-to-date documentation and code examples for any programming library or framework. Provides context-aware answers with official references.

**Official Documentation**: [context7-mcp](https://github.com/upstash/context7)

**Claude Code CLI Installation**:

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
```

If you have the `CONTEXT7_API_KEY` environment variable set, you can install the server with:

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp --api-key ${CONTEXT7_API_KEY}
```

---

## Language-Specific Tools

### dart

**Purpose**: Dart and Flutter development tools integration. Provides direct access to Dart analysis, testing, hot reload, and widget inspection.

**Features**:

- Dart/Flutter project analysis
- Hot reload for Flutter apps
- Widget tree inspection
- Test execution
- Pub package management
- Runtime error tracking

**Official Documentation**: [Dart MCP Server](https://dart.dev/tools/dart-tooling-dap)

**Claude Code CLI Installation**:

```bash
claude mcp add dart -- dart run dart mcp-server
```

---

## File System & Git Operations

### filesystem (Official MCP Server)

**Purpose**: Node.js server implementing MCP for filesystem operations with flexible directory access control.

**Features**:

- Read/write files with advanced edit_file support
- Create/list/delete directories
- Move files and directories
- Search files with glob patterns
- Get file metadata and directory trees
- Dynamic directory access via [MCP Roots](https://modelcontextprotocol.io/docs/learn/client-concepts#roots)

**Official Documentation**: [mcp-server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)

**Claude Code CLI Installation**:

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/dir
```

**Tools**: `read_text_file`, `write_file`, `edit_file`, `create_directory`, `list_directory`, `search_files`, `directory_tree`, `move_file`, `get_file_info`

---

### git (Official MCP Server)

**Purpose**: Git repository interaction and automation. Currently in early development.

**Features**:

- View git status and diffs
- Stage files and create commits
- Branch creation and checkout
- Commit log viewing
- Show commit contents

**Official Documentation**: [mcp-server-git](https://github.com/modelcontextprotocol/servers/tree/main/src/git)

**Claude Code CLI Installation**:

```bash
claude mcp add git -- uvx mcp-server-git --repository /path/to/git/repo
```

**Tools**: `git_status`, `git_diff_unstaged`, `git_diff_staged`, `git_diff`, `git_commit`, `git_add`, `git_reset`, `git_log`, `git_create_branch`, `git_checkout`, `git_show`, `git_branch`

---

## Web Access

### fetch (Official MCP Server)

**Purpose**: Fetches URLs from the internet and converts HTML to markdown. Enables LLMs to retrieve and process web content.

**Features**:

- URL fetching with HTML to markdown conversion
- Chunked reading via `start_index` parameter
- Configurable max length and timeout
- Raw content option
- robots.txt support (configurable)
- Custom user-agent support

**Official Documentation**: [mcp-server-fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)

**Claude Code CLI Installation**:

```bash
claude mcp add fetch -- uvx mcp-server-fetch
```

**Tools**: `fetch` (with prompt: `fetch`)

---

## Advanced Reasoning

### sequential-thinking (Official MCP Server)

**Purpose**: Provides structured, multi-step reasoning through Chain of Thought technique for dynamic and reflective problem-solving.

**Features**:

- Break down complex problems into manageable steps
- Revise and refine thoughts as understanding deepens
- Branch into alternative reasoning paths
- Adjust total thought count dynamically
- Generate and verify solution hypotheses

**Official Documentation**: [server-sequential-thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)

**Claude Code CLI Installation**:

```bash
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
```

**Tools**: `sequential_thinking`

**Parameters**:

- `thought` (string): Current thinking step
- `nextThoughtNeeded` (boolean): Whether another thought is needed
- `thoughtNumber` (integer): Current thought number
- `totalThoughts` (integer): Estimated total thoughts
- `isRevision` (boolean): Whether this revises previous thinking
- `revisesThought` (integer): Which thought is being reconsidered
- `branchFromThought` (integer): Branching point
- `branchId` (string): Branch identifier

---

## Memory & Knowledge

### memory (Official MCP Server)

**Purpose**: Persistent memory using a local knowledge graph. Enables Claude to remember information across chats.

**Features**:

- Entity creation with types (person, organization, event)
- Observation storage per entity
- Directed relations between entities
- Graph search and traversal
- OpenAI-style knowledge graph API

**Official Documentation**: [server-memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)

**Claude Code CLI Installation**:

```bash
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
```

**Tools**: `create_entities`, `create_relations`, `add_observations`, `delete_entities`, `delete_observations`, `delete_relations`, `read_graph`, `search_nodes`, `open_nodes`

**Environment Variables**:

- `MEMORY_FILE_PATH`: Path to memory storage (default: `memory.jsonl`)

---

## Time & Utilities

### time (Official MCP Server)

**Purpose**: Time and timezone conversion capabilities using IANA timezone names with automatic system timezone detection.

**Features**:

- Get current time in any timezone
- Convert time between timezones
- Automatic system timezone detection
- DST (Daylight Saving Time) support

**Official Documentation**: [mcp-server-time](https://github.com/modelcontextprotocol/servers/tree/main/src/time)

**Claude Code CLI Installation**:

```bash
claude mcp add time -- uvx mcp-server-time
```

**Tools**: `get_current_time`, `convert_time`

---

## Zhipu AI Services

The following MCP servers are powered by Zhipu AI (BigModel) and require an API key.

### web-reader (Zhipu)

**Purpose**: Fetches and converts web pages into LLM-friendly input with markdown formatting.

**Features**:

- Web page fetching and conversion
- Markdown output format
- Image handling options
- Link and image summaries

**Endpoint**: `https://open.bigmodel.cn/api/mcp/web_reader/mcp`

**API Key Required**: Yes (Zhipu AI)

**Claude Code CLI Installation** (requires API key in config):

```bash
# Add to claude.json manually with API key
```

---

### web-search-prime (Zhipu)

**Purpose**: Web search service with enhanced result formatting including summaries and metadata.

**Features**:

- Web page title and URL extraction
- Page summaries
- Website icons and metadata
- Domain filtering options
- Time-based search filters (oneDay, oneWeek, oneMonth, oneYear, noLimit)

**Endpoint**: `https://open.bigmodel.cn/api/mcp/web_search_prime/mcp`

**API Key Required**: Yes (Zhipu AI)

**Claude Code CLI Installation** (requires API key in config):

```bash
# Add to claude.json manually with API key
```

---

### zai-mcp-server (Zhipu)

**Purpose**: Advanced image and video analysis using AI vision models with specialized tools for visual content.

**Features**:

- UI screenshot to code conversion
- Text extraction from screenshots (OCR)
- Error diagnosis from screenshots
- Technical diagram understanding
- Data visualization analysis
- Video content analysis

**Official Documentation**: [zai-mcp-server](https://github.com/zai-ai/mcp-server)

**Claude Code CLI Installation** (requires `Z_AI_API_KEY` env variable):

```bash
claude mcp add zai-mcp-server -- npx -y @z_ai/mcp-server
```

**API Key Required**: Yes (Zhipu AI - `Z_AI_API_KEY` environment variable)

---

### zread (Zhipu)

**Purpose**: GitHub repository exploration and code reading without cloning.

**Features**:

- Repository structure inspection
- File content reading
- Documentation search
- Commit and issue search

**Endpoint**: `https://open.bigmodel.cn/api/mcp/zread/mcp`

**API Key Required**: Yes (Zhipu AI)

**Claude Code CLI Installation** (requires API key in config):

```bash
# Add to claude.json manually with API key
```

---

## Configuration

All MCP servers are configured in `claude.json`. For Zhipu AI services, replace `{API_KEY}` with your actual Zhipu AI API key.

### Claude Desktop Configuration Example

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/path/to/git/repo"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time"]
    }
  }
}
```

### Obtaining Zhipu AI API Key

Visit [BigModel.cn](https://open.bigmodel.cn/) to register and obtain your API key.

---

## Summary Table

| MCP Server          | Type  | API Key     | Primary Use            | Source      |
| ------------------- | ----- | ----------- | ---------------------- | ----------- |
| chrome-devtools     | stdio | No          | Browser automation     | Third-party |
| context7            | stdio | No          | Documentation lookup   | Third-party |
| dart                | stdio | No          | Dart/Flutter dev tools | Dart SDK    |
| filesystem          | stdio | No          | File operations        | Official    |
| fetch               | stdio | No          | URL fetching           | Official    |
| git                 | stdio | No          | Git operations         | Official    |
| memory              | stdio | No          | Knowledge graph        | Official    |
| sequential-thinking | stdio | No          | Structured reasoning   | Official    |
| time                | stdio | No          | Time/timezone          | Official    |
| web-reader          | HTTP  | Yes (Zhipu) | Web page reading       | Zhipu       |
| web-search-prime    | HTTP  | Yes (Zhipu) | Web search             | Zhipu       |
| zai-mcp-server      | stdio | Yes (Zhipu) | Image/video analysis   | Zhipu       |
| zread               | HTTP  | Yes (Zhipu) | GitHub repo reading    | Zhipu       |

---

## Additional Official MCP Servers

The official [MCP servers repository](https://github.com/modelcontextprotocol/servers) contains additional servers not configured in this environment:

- **everything**: Combined server with filesystem, git, and memory
- **postgres**: PostgreSQL database interaction

---

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

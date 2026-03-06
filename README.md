# github-ai-coding-agent-config

AI 编码工具配置集合，包含 Codex、Claude 与 `AGENTS.md` 模板，以及常用 Skills。

## 配置

### Codex 配置

- 模板文件：`codex/config.toml`
- 目标路径：`~/.codex/config.toml`
- 用途：配置模型、审批策略、sandbox、features、多 Agent 限制等

```bash
mkdir -p ~/.codex
[ -f ~/.codex/config.toml ] && cp ~/.codex/config.toml ~/.codex/config.toml.bak
cp ./codex/config.toml ~/.codex/config.toml
```

### Claude 配置

- 模板文件：`claude/settings.json`
- 目标路径：`~/.claude/settings.json`
- 用途：配置模型、审批策略、sandbox、features、多 Agent 限制等

```bash
mkdir -p ~/.claude
[ -f ~/.claude/settings.json ] && cp ~/.claude/settings.json ~/.claude/settings.json.bak
cp ./claude/settings.json ~/.claude/settings.json
```

### `AGENTS.md`

- 模板文件：`codex/AGENTS.md`
- 推荐路径：`~/.agents/AGENTS.md`（作为主文件）
- 联动方式：将 `~/.codex/AGENTS.md` 软链接到主文件，避免多份配置漂移

```bash
mkdir -p ~/.agents ~/.codex
cp ./codex/AGENTS.md ~/.agents/AGENTS.md
rm -f ~/.codex/AGENTS.md
ln -s ~/.agents/AGENTS.md ~/.codex/AGENTS.md
```

## Skills

### 我的 Skills

- `lint-agents-md`：评估 `AGENTS.md` 质量，并自动检测常见设计错误与重写建议

### 开源 Skills

- 首次使用执行 `uv sync` 初始化 Python 环境
- 使用 `uv run python ./scripts/update.py` 下载并更新技能到本地（支持自动识别 Skills 目录与技能组合包）

**安装到 AI 助手**

```bash
# 1. 默认安装 (安装 ./skills 目录下的标准技能)
./scripts/install.sh

# 2. 安装指定技能包 (例如 ./flutter-skills)
./scripts/install.sh flutter-skills

# 3. 安装所有技能 (./skills 及所有 *-skills 目录)
./scripts/install.sh all
```

默认安装位置：

- 源文件：`~/.agents/skills`
- 软链接：`~/.claude/skills` (供 Claude 使用)

**技能列表**

- [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)：创建自定义技能
- [mcp-builder](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)：构建自定义 MCP 技能
- [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx)：与 Excel 文件交互
- [code-simplifier](https://github.com/simonwong/agent-skills/tree/main/skills/code-simplifier)：简化代码，提高可读性
- [chrome-devtools](https://github.com/github/awesome-copilot/tree/main/skills/chrome-devtools)：与 Chrome DevTools MCP 交互
- [create-agentsmd](https://github.com/github/awesome-copilot/tree/main/skills/create-agentsmd)：创建 `AGENTS.md` 文件
- [create-readme](https://github.com/github/awesome-copilot/tree/main/skills/create-readme)：创建 `README.md` 文件
- [create-specification](https://github.com/github/awesome-copilot/tree/main/skills/create-specification)：创建规范文档（保存到 `spec/`，命名格式 `spec-[a-z0-9-]+.md`）
- [create-technical-spike](https://github.com/github/awesome-copilot/tree/main/skills/create-technical-spike)：创建技术探索文档
- [editorconfig](https://github.com/github/awesome-copilot/tree/main/skills/editorconfig)：生成符合最佳实践的 `.editorconfig`
- [excalidraw-diagram-generator](https://github.com/github/awesome-copilot/tree/main/skills/excalidraw-diagram-generator)：基于描述生成 Excalidraw 图表
- [git-commit](https://github.com/github/awesome-copilot/tree/main/skills/git-commit)：基于 Conventional Commits 生成标准提交
- [refactor](https://github.com/github/awesome-copilot/tree/main/skills/refactor)：在保持行为不变前提下重构代码
- [sql-optimization](https://github.com/github/awesome-copilot/tree/main/skills/sql-optimization)：优化 SQL 查询性能
- [changelog-automation](https://github.com/wshobson/agents/tree/main/plugins/documentation-generation/skills/changelog-automation)：基于提交历史和标签自动生成变更日志
- [read-github](https://github.com/am-will/codex-skills/tree/main/skills/read-github)：通过 gitmcp.io MCP 服务访问 GitHub 仓库文档和代码
- [markdown-url](https://github.com/am-will/codex-skills/tree/main/skills/markdown-url)：在 URL 前添加前缀，通过 markdown.new 浏览网站
- [agent-browser](https://github.com/vercel-labs/agent-browser/tree/main/skills/agent-browser)：浏览器自动化交互（需安装插件）
- [browser-use](https://github.com/browser-use/browser-use/tree/main/skills/browser-use)：浏览器自动化执行任务（需安装插件）
- [humanizer-zh](https://github.com/op7418/humanizer-zh)：AI 写作去痕工具（中文版）
- [flutter-skills](https://github.com/flutter/skills)：Flutter 开发技能集合

### Superpowers

[Superpowers](https://github.com/obra/superpowers) 是一组完整开发技能集合，建议整体安装，不要单独拆分安装。

**Claude Code 安装**

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**Codex 安装**

将下面这句话直接发送给 Codex：

```bash
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.codex/INSTALL.md
```

## License

本项目采用 [MIT License](./LICENSE)。

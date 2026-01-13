.PHONY: all install install-skills install-mcp uninstall uninstall-skills uninstall-mcp \
        list list-skills list-mcp diff diff-mcp backups restore help

# Default target
all: install

# Install everything (skills + MCP servers)
install: install-skills install-mcp

# Install skills
install-skills:
	@echo "Installing skills..."
	@python3 scripts/skills.py install

# Install MCP servers (from mcp/claude.json)
install-mcp:
	@echo "Installing MCP servers..."
	@python3 scripts/mcp.py install

# Uninstall everything
uninstall: uninstall-skills uninstall-mcp

# Uninstall skills
uninstall-skills:
	@echo "Uninstalling skills..."
	@python3 scripts/skills.py uninstall

# Uninstall MCP servers
uninstall-mcp:
	@echo "Uninstalling MCP servers..."
	@python3 scripts/mcp.py uninstall

# List everything
list: list-skills list-mcp

# List skills
list-skills:
	@python3 scripts/skills.py list

# List MCP servers
list-mcp:
	@python3 scripts/mcp.py list

# Show differences for MCP servers
diff: diff-mcp

diff-mcp:
	@python3 scripts/mcp.py diff

# List backups
backups:
	@python3 scripts/mcp.py backups

# Restore from backup (usage: make restore BACKUP=claude.json.20250113_123456)
restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "Usage: make restore BACKUP=claude.json.20250113_123456"; \
		echo "Run 'make backups' to see available backups"; \
		exit 1; \
	fi
	@python3 scripts/mcp.py restore $(BACKUP)

# Force reinstall skills
reinstall-skills:
	@echo "Force reinstalling skills..."
	@python3 scripts/skills.py install -f

# Force reinstall MCP servers
reinstall-mcp:
	@echo "Force reinstalling MCP servers..."
	@python3 scripts/mcp.py install -f

# Dry run for MCP installation
dry-run-mcp:
	@echo "Dry run for MCP installation..."
	@python3 scripts/mcp.py install --dry-run

# Install MCP without backup
install-mcp-no-backup:
	@echo "Installing MCP servers (no backup)..."
	@python3 scripts/mcp.py install --no-backup

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Installation:"
	@echo "  make install             - Install skills and MCP servers"
	@echo "  make install-skills      - Install skills only"
	@echo "  make install-mcp         - Install MCP servers only"
	@echo "  make install-mcp-no-backup - Install MCP without backup"
	@echo ""
	@echo "Uninstallation:"
	@echo "  make uninstall           - Uninstall skills and MCP servers"
	@echo "  make uninstall-skills    - Uninstall skills only"
	@echo "  make uninstall-mcp       - Uninstall MCP servers only"
	@echo ""
	@echo "Listing:"
	@echo "  make list                - List skills and MCP servers"
	@echo "  make list-skills         - List skills only"
	@echo "  make list-mcp            - List MCP servers only"
	@echo "  make backups             - List MCP config backups"
	@echo ""
	@echo "Maintenance:"
	@echo "  make reinstall-skills    - Force reinstall all skills"
	@echo "  make reinstall-mcp       - Force reinstall all MCP servers"
	@echo "  make diff                - Show MCP config differences"
	@echo "  make dry-run-mcp         - Preview MCP installation"
	@echo "  make restore BACKUP=...  - Restore from backup"
	@echo ""
	@echo "Direct script usage:"
	@echo "  python3 scripts/skills.py install|uninstall|list"
	@echo "  python3 scripts/mcp.py install|uninstall|list|diff|backups|restore"

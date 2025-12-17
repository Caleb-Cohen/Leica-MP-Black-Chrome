# Leica MP Stock Monitor

Monitor retailer listings for the Leica MP Black Chrome and send Discord alerts whenever new matches appear.

**Current Status: Phase 0 (Scaffolding)** - This project is being developed in phases. Currently, only the basic project structure, configuration, logging, and CLI entry point are implemented.

## Development Phases

- **Phase 0** (Current): Minimal scaffolding - project structure, config loader, logging, CLI entry point
- **Phase 1**: Single retailer scraper with console output
- **Phase 2**: Local state persistence and deduplication
- **Phase 3**: Discord webhook notifications
- **Phase 4**: Second retailer and shared abstractions
- **Phase 5**: Docker and Synology deployment

## Quick Start

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. (Optional) Copy `.env.example` to `.env` for configuration:
   ```bash
   cp .env.example .env
   ```

3. Run the monitor:
   ```bash
   python3 -m monitor
   ```

**Note:** Phase 0 is a placeholder that logs startup/shutdown messages. No scraping, notifications, or persistence is implemented yet.

## Configuration

Configuration is loaded from a `.env` file (optional in Phase 0). See `.env.example` for available options. Configuration variables will be added in later phases:

- **Phase 1**: `POLL_INTERVAL_SECONDS` - Poll interval in seconds
- **Phase 2**: `STATE_FILE_PATH` - Path to state persistence file
- **Phase 3**: `DISCORD_WEBHOOK_URL` - Discord webhook endpoint

## Project Structure

```
monitor/
  ├── __init__.py      # Logging configuration
  ├── __main__.py      # CLI entry point
  ├── cli.py           # Main run() function
  ├── config.py        # Configuration loader
  └── scrapers/        # (Phase 1+) Retailer scrapers
```

## Requirements

- Python 3.12+
- `python-dotenv` (for .env file loading)

**Development dependencies** (optional, for linting/formatting):
- Install with: `pip install -r requirements-dev.txt`

## Development

### Linting and Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and code formatting.

**Check for issues:**
```bash
python3 -m ruff check monitor/
```

**Auto-fix issues:**
```bash
python3 -m ruff check --fix monitor/
```

**Format code:**
```bash
python3 -m ruff format monitor/
```

**Check and format in one command:**
```bash
python3 -m ruff check --fix monitor/ && python3 -m ruff format monitor/
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to automatically run Ruff linting and formatting before each commit.

**First-time setup:**
```bash
# Install development dependencies (includes pre-commit)
pip install -r requirements-dev.txt

# Install git hooks
pre-commit install
```

After installation, pre-commit will automatically:
- Run Ruff linting (with auto-fix)
- Run Ruff formatting

on every `git commit`. If issues are found, the commit will be blocked until they're fixed.

**Run hooks manually (without committing):**
```bash
pre-commit run --all-files
```

**Skip hooks (not recommended):**
```bash
git commit --no-verify
```

## Future Features

- Poll multiple Leica retailers (`mapcamera.com`, `tamarkin.com`, `camerawest.com`, `kitamuracamera.jp`)
- Filter listings for "Leica MP" plus Black Chrome keyword variants
- Deduplicate alerts with on-disk state tracking
- Discord webhook notifications
- Docker setup for Synology NAS deployment


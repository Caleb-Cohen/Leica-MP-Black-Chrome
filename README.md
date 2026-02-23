# Leica MP Black Chrome Stock Monitor

Polls three camera retailers/forums for Leica MP Black Chrome listings and sends Discord alerts when new matches appear. Designed to run on a Hetzner VPS via Docker.

## Sources

- **Camera West** — Shopify search API (`camerawest.com`)
- **MapCamera** — HTML scraping (`mapcamera.com`, Japanese retailer)
- **Fred Miranda** — Buy & Sell forum thread titles (`fredmiranda.com/forum/board/10/`)

## How It Works

1. Each poll cycle scrapes all three sources for listings mentioning "Leica MP"
2. Filters results to match Black Chrome finish — rejects Black Paint, M-P (digital), and MP-240
3. Checks against a local state file to find only *new* listings
4. Sends a Discord status embed every cycle showing what was checked and match counts
5. Tags your Discord user when a new Leica MP Black Chrome is found

## Setup

1. Copy the example env file and fill in your values:
   ```bash
   cp .env.example .env
   ```

2. Run with Docker Compose:
   ```bash
   docker compose up -d --build
   ```

3. Check logs:
   ```bash
   docker compose logs -f
   ```

## Configuration

All config is via `.env` (or environment variables in Docker).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_WEBHOOK_URL` | Yes | — | Discord webhook endpoint |
| `DISCORD_USER_ID` | Yes | — | Your Discord user ID (tagged on match) |
| `POLL_INTERVAL_SECONDS` | No | `300` | Seconds between poll cycles |

### Scraper URLs (optional overrides)

These have sensible defaults built in. Override only if a site changes its URL structure.

| Variable | Default |
|----------|---------|
| `CAMERAWEST_SEARCH_URL` | `https://camerawest.com/search/suggest.json` |
| `CAMERAWEST_SEARCH_QUERY` | `leica mp` |
| `CAMERAWEST_BASE_URL` | `https://camerawest.com/products/` |
| `MAPCAMERA_SEARCH_URL` | `https://www.mapcamera.com/search` |
| `MAPCAMERA_SEARCH_KEYWORD` | `leica mp` |
| `MAPCAMERA_BASE_URL` | `https://www.mapcamera.com` |
| `FREDMIRANDA_FORUM_URL` | `https://fredmiranda.com/forum/board/10/` |
| `FREDMIRANDA_BASE_URL` | `https://fredmiranda.com` |

## Project Structure

```
monitor/
├── __init__.py              # Logging setup
├── __main__.py              # Entry point
├── cli.py                   # Main polling loop
├── config.py                # Loads .env configuration
├── discord.py               # Discord webhook notifications
├── filtering.py             # Black Chrome vs Black Paint filter
├── state.py                 # JSON deduplication state
└── scrapers/
    ├── base.py              # Listing dataclass & base scraper
    ├── camerawest.py        # Camera West (Shopify JSON API)
    ├── mapcamera.py         # MapCamera (HTML parsing)
    └── fredmiranda.py       # Fred Miranda (forum thread titles)
Dockerfile
docker-compose.yml
```

## Development

Requires Python 3.12+. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # ruff, pre-commit
```

Run locally (needs a valid `.env`):
```bash
python -m monitor
```

Lint and format:
```bash
ruff check monitor/ && ruff format monitor/
```

Pre-commit hooks auto-run ruff on every commit:
```bash
pre-commit install
```

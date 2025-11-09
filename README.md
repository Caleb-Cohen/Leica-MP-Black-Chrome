# Leica MP Stock Monitor

Monitor retailer listings for the Leica MP Black Chrome and send Discord alerts whenever new matches appear.

## Features
- Polls multiple Leica retailers (`mapcamera.com`, `tamarkin.com`, `camerawest.com`, `kitamuracamera.jp`).
- Filters listings for “Leica MP” plus Black Chrome keyword variants, including mixed-language titles.
- Deduplicates alerts with on-disk state tracking.
- Ships with Docker setup for easy deployment on Synology NAS.

## Quick Start
1. Copy `.env.example` to `.env` and provide poll interval, Discord webhook URL, and any site overrides.
2. Install dependencies and run the monitor:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m monitor run
   ```

## Docker
1. Build the image:
   ```bash
   docker build -t leica-monitor .
   ```
2. Run on Synology (replace `/path/to/config` with your volume mapping):
   ```bash
   docker run -d --name leica-monitor --env-file /path/to/config/.env leica-monitor
   ```

## Configuration
- `DISCORD_WEBHOOK_URL`: Discord endpoint for stock alerts.
- `POLL_INTERVAL_SECONDS`: Interval between polls (defaults to 600).
- `SITE_*` vars: Optional per-site toggles, pagination limits, or locale overrides.

## Testing
```bash
pytest
```

## Roadmap
- Add more retailers and structured listing parsing.
- Extend keyword matching with fuzzy search and localized synonyms.
- Surface richer metadata (condition, price history, images) in alerts.


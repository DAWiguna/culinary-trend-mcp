# Culinary Trend MCP Server 🍳

A Model Context Protocol (MCP) server for monitoring culinary trends across web and social media platforms using SearXNG.

Designed for culinary schools to stay ahead of food trends and identify viral recipes, cooking techniques, and trending ingredients for new class development.

## Features

✨ **Trend Discovery**
- Search for trending culinary content across web and news
- Monitor social media platforms (TikTok, Instagram, Pinterest)
- Detect viral foods and recipes in real-time

📊 **Continuous Monitoring**
- Set up automatic trend monitoring
- Track changes and new discoveries
- Store monitoring history (up to 30 days)

🔍 **Pattern Detection**
- Analyze emerging culinary patterns
- Track trend velocity (rapidly growing, growing, stable)
- Identify platform distribution
- See which sources are trending

## Requirements

- Python 3.11+
- SearXNG running locally at `http://localhost:8090`
- Hermes agent (Nous Research)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DAWiguna/culinary-trend-mcp.git
cd culinary-trend-mcp
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Ensure SearXNG is Running

Make sure your local SearXNG instance is accessible at `http://localhost:8090`

## Configuration

Edit `config.py` to customize:

```python
# SearXNG endpoint
SEARXNG_URL = "http://localhost:8090"

# Default monitoring interval (minutes)
DEFAULT_CHECK_INTERVAL = 30

# Data retention period (days)
MONITORING_RETENTION_DAYS = 30

# Search result limits
DEFAULT_RESULT_LIMIT = 10
MAX_RESULT_LIMIT = 50
```

## Running the Server

```bash
python mcp_server.py
```

The server will:
1. Check SearXNG connectivity
2. Initialize the SQLite database
3. Start listening for MCP requests

## Available Tools

### 1. search_trending_food

Search for trending culinary content across the web and news.

**Parameters:**
- `query` (string, required): What to search for
- `limit` (integer, optional): Number of results (default: 10)

**Example:**
```json
{
  "method": "search_trending_food",
  "params": {
    "query": "viral sourdough bread",
    "limit": 15
  }
}
```

### 2. search_social_media

Search social media platforms for food trends.

**Parameters:**
- `query` (string, required): What to search for
- `platforms` (string, optional): "all" | "tiktok" | "instagram" | "pinterest" (default: "all")
- `limit` (integer, optional): Number of results (default: 10)

**Example:**
```json
{
  "method": "search_social_media",
  "params": {
    "query": "matcha desserts",
    "platforms": "tiktok",
    "limit": 20
  }
}
```

### 3. start_monitoring_trend

Start continuous monitoring of a culinary trend.

**Parameters:**
- `trend_name` (string, required): Name of the trend
- `query` (string, optional): Custom search query
- `platforms` (string, optional): Platforms to monitor (default: "all")
- `check_interval_minutes` (integer, optional): Check frequency (default: 30)
- `notes` (string, optional): Additional notes

**Example:**
```json
{
  "method": "start_monitoring_trend",
  "params": {
    "trend_name": "Fermented Vegetables",
    "query": "trending fermented foods",
    "platforms": "all",
    "check_interval_minutes": 60,
    "notes": "For new pickling class"
  }
}
```

### 4. stop_monitoring_trend

Stop monitoring a specific trend.

**Parameters:**
- `monitoring_id` (string, required): The monitoring task ID

### 5. get_active_monitors

Get list of all currently active monitors.

### 6. get_trend_alerts

Get recent alerts and discovered items.

**Parameters:**
- `limit` (integer, optional): Number of alerts (default: 20)

### 7. get_monitoring_history

Get historical data for a monitored trend.

**Parameters:**
- `trend_name` (string, required): The trend name
- `days` (integer, optional): Days to look back (default: 7)

### 8. detect_patterns

Analyze and detect emerging patterns in a trend.

**Parameters:**
- `trend_name` (string, required): The trend name

**Returns:**
```json
{
  "total_items": 45,
  "trend_velocity": "rapidly_growing",
  "emerging_sources": ["tiktok", "instagram"],
  "platform_distribution": {
    "tiktok": 28,
    "instagram": 15,
    "pinterest": 2
  }
}
```

## Integration with Hermes

Configure Hermes to connect to this MCP server:

### For Hermes CLI

```json
{
  "mcp_servers": {
    "culinary_trends": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "SEARXNG_URL": "http://localhost:8090"
      }
    }
  }
}
```

### Using Hermes

Once integrated, you can use it in Hermes:

```
Hermes: "Find viral bread trends on TikTok this week"
→ Uses: search_social_media("bread trends", platforms="tiktok")

Hermes: "Start monitoring fermented food trends"
→ Uses: start_monitoring_trend("Fermented Foods", query="trending fermented foods")

Hermes: "What patterns are emerging in matcha desserts?"
→ Uses: detect_patterns("Matcha Desserts")

Hermes: "Show me this week's culinary trend alerts"
→ Uses: get_trend_alerts(limit=25)
```

## Database

The server uses SQLite to store:

- **monitors** - Active and inactive monitoring tasks
- **search_results** - All discovered trend items
- **alerts** - Alerts and changes detected
- **trend_analysis** - Pattern analysis data

Database file: `culinary_trends.db` (created automatically)

### Data Retention

Old data is automatically cleaned up based on `MONITORING_RETENTION_DAYS` configuration (default: 30 days).

## Project Structure

```
culinary-trend-mcp/
├── mcp_server.py          # Main MCP server
├── config.py              # Configuration settings
├── searxng_client.py      # SearXNG API client
├── trend_monitor.py       # Monitoring engine
├── database.py            # SQLite database
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignores
├── README.md             # This file
└── culinary_trends.db    # SQLite database (created on first run)
```

## Logging

Logs are written to:
- **Console**: Real-time status updates
- **File**: `culinary_trends.log` for historical records

Control log level via `config.py`:

```python
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### SearXNG Connection Failed

```
Error: SearXNG not responding at http://localhost:8090
```

**Solution:**
- Verify SearXNG is running: `curl http://localhost:8090`
- Check SearXNG logs for errors
- Verify network connectivity

### Database Locked

```
Error: database is locked
```

**Solution:**
- Ensure only one MCP server instance is running
- Delete `culinary_trends.db` and restart if corrupted

### No Results from Searches

**Solution:**
- Try different search terms
- Verify SearXNG has internet connectivity
- Check SearXNG's configured search engines

## Use Cases for Culinary Schools

### Discover New Class Ideas
```
"Find what's currently viral in baking and pastry"
→ Automatically discovers trending techniques
```

### Stay Current with Food Trends
```
"Monitor trending fermented foods on Pinterest for 2 weeks"
→ Gets alerts on emerging fermented food trends
```

### Research Student Interest
```
"What bread-making techniques are trending on TikTok?"
→ Identifies student interest areas
```

### Develop Curriculum
```
"Show me emerging patterns in molecular gastronomy"
→ Analyzes what's gaining momentum
```

## Performance Tips

- Set reasonable check intervals (30-120 minutes for most trends)
- Limit results to necessary amount (10-20 per search)
- Use specific keywords for better results
- Monitor 5-10 trends simultaneously for optimal performance

## License

MIT License - feel free to use and modify

## Support

For issues or feature requests, please check:
1. SearXNG is running and accessible
2. Python 3.11+ is installed
3. All dependencies are installed: `pip install -r requirements.txt`
4. Database permissions are correct

---

**Built for culinary schools to stay ahead of food trends! 🍳✨**

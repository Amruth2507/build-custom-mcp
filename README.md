# TMDB Model Context Protocol (MCP) Server

[![MCP Server](https://img.shields.io/badge/MCP-Server-blue?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/release/python-3100/)

A robust **Model Context Protocol (MCP)** server that seamlessly wraps [The Movie Database (TMDB) API](https://developer.themoviedb.org/docs/getting-started). This server enables Large Language Models (LLMs) and MCP-compatible clients (like Claude Desktop) to invoke specialized tools for exploring movie databases, fetching detailed cinematic data, and dynamically retrieving tailored film recommendations.

## 🌟 Key Features

This server currently exposes four native MCP tools:

- `search_movies`: Search for movies by title to retrieve a matching list of films alongside their TMDB IDs, release dates, and overviews.
- `get_movie_details`: Fetch comprehensive information about a specific movie, including its cast, runtime, tagline, average rating, and genres.
- `get_popular_movies`: Retrieve dynamically paging lists of the current most popular movies globally.
- `get_movie_recommendations`: Retrieve five intelligently tailored movie recommendations based on a previously selected movie ID.

## 🛠 Resilience & Architecture

- **Graceful Rate Limiting**: Properly traps HTTP `429 Too Many Requests` when TMDB rate limits are exceeded, presenting clean contextual errors back to the caller instead of crashing.
- **Strict STDIO Transport**: Ensures no arbitrary stdout pollution occurs so that the standard input/output streams needed for the MCP binary protocol remain pristine.
- **Authentication Protected**: Built to enforce API keys implicitly via environment variables, safeguarding your private API credentials from being logged payload contents.
- **Mock Demo Mode**: Built-in mock testing so you can evaluate the agent capabilities locally before you register for an official API token.

---

## 🚀 Getting Started

### Prerequisites

1. Python 3.10 or higher.
2. A free **TMDB API Read Access Token**. 
   - You can get one by [signing up for a TMDB account](https://www.themoviedb.org/signup) and generating an API token under the Settings > API section.

### Installation

1. Clone this repository directly to your machine:
```bash
git clone https://github.com/your-username/building-a-custom-mcp.git
cd building-a-custom-mcp
```

2. Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

*(Note: The environment relies on the official `mcp` SDK and `httpx` to facilitate robust asynchronous API requests.)*

---

## 🎮 Running the Demo Script

We included a programmatic client script (`demo.py`) that boots up an isolated MCP session natively and runs test calls against all of the created tools.

To run the live demo with your API key:
```bash
# macOS/Linux
export TMDB_API_KEY="your_jwt_token_here"
python demo.py

# Windows Command Prompt
set TMDB_API_KEY=your_jwt_token_here
python demo.py

# Windows PowerShell
$env:TMDB_API_KEY="your_jwt_token_here"
python demo.py
```

### Mock Testing
If you don't have a TMDB key on hand but want to see the exact structural output, you can run the application in "Mock Demo Mode":
```bash
# Windows
set TMDB_API_KEY=demo
python demo.py
```

---

## 🧩 Integrating with Claude Desktop

To run this server permanently inside Claude Desktop, simply inject this application into your Claude MCP configuration file.

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add a new server definition to the `mcpServers` object. Provide the **absolute path** to your `server.py` script and your TMDB token:

```json
{
  "mcpServers": {
    "tmdb": {
      "command": "python",
      "args": [
        "C:\\absolute\\path\\to\\building-a-custom-mcp\\server\\server.py"
      ],
      "env": {
        "TMDB_API_KEY": "YOUR_TMDB_READ_ACCESS_TOKEN_HERE"
      }
    }
  }
}
```

> **Note**: For Windows paths, ensure backward slashes are explicitly escaped (e.g., `C:\\Users\\...`). 

---

## 🤝 Contributing
Feel free to open Issues or submit Pull Requests for expansions—such as adding tools for fetching TV shows, actor portfolios, or user reviews!

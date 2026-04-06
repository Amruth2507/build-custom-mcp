import asyncio
import os
import sys

# We'll use the official mcp python SDK to programmatically spawn and interact with the server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_demo():
    print("🎬 Starting TMDB MCP Server Demo...\n")
    
    # Path to our server script
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "server", "server.py"))
    
    # We retrieve the key from our local demo environment
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
         print("❌ DEMO FAILED!")
         print("You must set the TMDB_API_KEY environment variable to run this demo.")
         print("Example: set TMDB_API_KEY=your_token_here")
         sys.exit(1)
    
    # Define how to span our python standard IO server
    server_params = StdioServerParameters(
        command=sys.executable, # Uses the current python interpreter
        args=[server_path],
        env=os.environ.copy() # Passes our API key to the server
    )

    print("🔌 Booting MCP server via STDIO...")
    # Initialize the standard IO client
    async with stdio_client(server_params) as (read_process, write_process):
        # Create an MCP session with the server
        async with ClientSession(read_process, write_process) as session:
            await session.initialize()
            print("✅ Server Initialized successfully!\n")

            # --- Tool 1: get_popular_movies ---
            print("📝 Action 1: Asking the server for Popular Movies via 'get_popular_movies' tool...")
            try:
                result = await session.call_tool("get_popular_movies", {"page": 1})
                if result.content:
                    print(result.content[0].text)
                    print()
            except Exception as e:
                 print(f"Tool error: {e}")

            # --- Tool 2: search_movies ---
            # Let's search for "Inception"
            query = "Inception"
            print(f"📝 Action 2: Searching for movie '{query}' via 'search_movies' tool...")
            movie_id = None
            try:
                result = await session.call_tool("search_movies", {"query": query, "page": 1})
                if result.content:
                    print(result.content[0].text)
                    print()
                    # We know inception's ID is usually 27205, but we can extract it if we parsed it. 
                    # For demo purposes, we'll hardcode the known ID for the next steps or simply use 27205
            except Exception as e:
                 print(f"Tool error: {e}")

            # --- Tool 3: get_movie_details ---
            m_id = 27205 # Inception ID
            print(f"📝 Action 3: Fetching details for ID {m_id} via 'get_movie_details' tool...")
            try:
                result = await session.call_tool("get_movie_details", {"movie_id": m_id})
                if result.content:
                    print(result.content[0].text)
                    print()
            except Exception as e:
                 print(f"Tool error: {e}")
                 
            # --- Tool 4: get_movie_recommendations ---
            print(f"📝 Action 4: Getting recommendations for ID {m_id} via 'get_movie_recommendations' tool...")
            try:
                result = await session.call_tool("get_movie_recommendations", {"movie_id": m_id})
                if result.content:
                    print(result.content[0].text)
                    print()
            except Exception as e:
                 print(f"Tool error: {e}")

            print("🎉 Demo complete. The MCP architecture successfully handled standard remote API integration!")

if __name__ == "__main__":
    asyncio.run(run_demo())

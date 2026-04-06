import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP

# Retrieve the TMDB API key from the environment
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    print("Error: TMDB_API_KEY environment variable is required to run this server.", file=sys.stderr)
    print("Use 'demo' as the key to run in mocked local demo mode.", file=sys.stderr)
    sys.exit(1)

# Initialize FastMCP Server
mcp = FastMCP("TMDB Movies Server")

BASE_URL = "https://api.themoviedb.org/3"

# Common HTTP Headers required by TMDB HTTP API using Bearer Token
HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}

# Timeout/Retries configuration for httpx to handle resilience
timeout = httpx.Timeout(10.0, connect=5.0)

async def make_tmdb_request(client: httpx.AsyncClient, endpoint: str, params: dict = None) -> dict:
    """Helper method to handle TMDB API requests with simple rate limit and error handling."""
    
    # ------------------ MOCK MODE FOR DEMONSTRATION ------------------
    if TMDB_API_KEY == "demo":
        if endpoint == "/movie/popular":
            return {"results": [{"id": 550, "title": "Fight Club", "release_date": "1999-10-15", "vote_average": 8.4}, {"id": 27205, "title": "Inception", "release_date": "2010-07-15", "vote_average": 8.4}]}
        elif endpoint == "/search/movie":
            query = params.get("query", "").lower()
            return {"results": [{"id": 27205, "title": "Inception", "release_date": "2010-07-15", "vote_average": 8.4, "overview": "Cobb, a skilled thief who commits corporate espionage..."}]}
        elif "/recommendations" in endpoint:
            return {"results": [{"id": 157336, "title": "Interstellar", "release_date": "2014-11-05"}, {"id": 155, "title": "The Dark Knight", "release_date": "2008-07-16"}]}
        elif endpoint.startswith("/movie/"):
            return {
                "title": "Inception", "tagline": "Your mind is the scene of the crime.", "release_date": "2010-07-15",
                "runtime": 148, "vote_average": 8.4, "overview": "Cobb, a skilled thief...",
                "genres": [{"name": "Action"}, {"name": "Science Fiction"}],
                "credits": {"cast": [{"name": "Leonardo DiCaprio"}, {"name": "Joseph Gordon-Levitt"}]}
            }
    # -----------------------------------------------------------------

    url = f"{BASE_URL}{endpoint}"
    try:
        response = await client.get(url, headers=HEADERS, params=params, timeout=timeout)
        
        if response.status_code == 429:
            raise ValueError("Rate limit exceeded for TMDB API. Please try again later.")
            
        # Raise for other HTTP errors (4xx, 5xx)
        response.raise_for_status()
        
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("Unauthorized. Please check your TMDB_API_KEY.")
        elif e.response.status_code == 404:
            raise ValueError(f"Resource not found at {endpoint}")
        else:
            raise ValueError(f"TMDB API error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Network error connecting to TMDB: {str(e)}")

@mcp.tool()
async def search_movies(query: str, page: int = 1) -> str:
    """
    Search for movies by their title.
    
    Args:
        query: The search query string (e.g., 'Inception', 'Star Wars').
        page: The page number of results to retrieve.
    """
    params = {
        "query": query,
        "page": page,
        "include_adult": False,
        "language": "en-US",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            data = await make_tmdb_request(client, "/search/movie", params)
            
            results = data.get("results", [])
            if not results:
                return f"No movies found matching '{query}'."
                
            output = []
            for item in results[:5]: # Return top 5 matches
                title = item.get("title", 'Unknown')
                release_date = item.get("release_date", 'N/A')
                vote_avg = item.get("vote_average", 'N/A')
                movie_id = item.get("id")
                overview = item.get("overview", "")
                
                output.append(
                    f"Title: {title} ({release_date})\n"
                    f"ID: {movie_id} | Rating: {vote_avg}/10\n"
                    f"Overview: {overview[:150]}...\n"
                )
            return "\n".join(output)
            
        except Exception as e:
            return f"Error searching movies: {str(e)}"

@mcp.tool()
async def get_movie_details(movie_id: int) -> str:
    """
    Get detailed information about a specific movie by its TMDB ID.
    
    Args:
        movie_id: The unique TMDB ID of the movie (can be found using search_movies).
    """
    async with httpx.AsyncClient() as client:
        try:
            # Append credits to retrieve cast list in one request
            data = await make_tmdb_request(client, f"/movie/{movie_id}", {"append_to_response": "credits"})
            
            title = data.get("title", 'Unknown')
            tagline = data.get("tagline", '')
            release_date = data.get("release_date", 'N/A')
            runtime = data.get("runtime", 'N/A')
            vote_avg = data.get("vote_average", 'N/A')
            overview = data.get("overview", "")
            
            genres = ", ".join([g.get("name", "") for g in data.get("genres", [])])
            
            cast_list = data.get("credits", {}).get("cast", [])
            top_cast = ", ".join([c.get("name", "") for c in cast_list[:5]])
            
            output = f"========== {title} ==========\n"
            if tagline:
                output += f"Tagline: {tagline}\n"
            output += f"Release Date: {release_date}\n"
            output += f"Runtime: {runtime} minutes\n"
            output += f"Rating: {vote_avg}/10\n"
            output += f"Genres: {genres}\n"
            output += f"Top Cast: {top_cast}\n"
            output += f"Overview:\n{overview}\n"
            output += str("===================================")
            
            return output
            
        except Exception as e:
            return f"Error retrieving movie details: {str(e)}"

@mcp.tool()
async def get_popular_movies(page: int = 1) -> str:
    """
    Get a list of the current popular movies on TMDB.
    
    Args:
        page: The page number of results to retrieve (default is 1).
    """
    params = {
        "page": page,
        "language": "en-US",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            data = await make_tmdb_request(client, "/movie/popular", params)
            
            results = data.get("results", [])
            if not results:
                return "No popular movies found at this time."
                
            output = ["========== Current Popular Movies =========="]
            for idx, item in enumerate(results[:10], 1): # Return top 10
                title = item.get("title", 'Unknown')
                release_date = item.get("release_date", 'N/A')
                vote_avg = item.get("vote_average", 'N/A')
                movie_id = item.get("id")
                
                output.append(
                    f"{idx}. {title} ({release_date}) - ID: {movie_id} | Rating: {vote_avg}/10"
                )
            output.append("==========================================")
            return "\n".join(output)
            
        except Exception as e:
            return f"Error retrieving popular movies: {str(e)}"

@mcp.tool()
async def get_movie_recommendations(movie_id: int) -> str:
    """
    Get a list of recommended movies for a movie.
    
    Args:
        movie_id: The unique TMDB ID of the original movie.
    """
    params = {
        "language": "en-US",
        "page": 1,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            data = await make_tmdb_request(client, f"/movie/{movie_id}/recommendations", params)
            
            results = data.get("results", [])
            if not results:
                return f"No recommendations found for movie ID {movie_id}."
                
            output = [f"========== Recommendations for Movie {movie_id} =========="]
            for idx, item in enumerate(results[:5], 1): # Return top 5
                title = item.get("title", 'Unknown')
                release_date = item.get("release_date", 'N/A')
                rec_id = item.get("id")
                
                output.append(f"{idx}. {title} ({release_date}) - ID: {rec_id}")
            output.append("======================================================")
            return "\n".join(output)
            
        except Exception as e:
            return f"Error retrieving recommendations: {str(e)}"

if __name__ == "__main__":
    # Start the server on stdio transport
    mcp.run(transport='stdio')

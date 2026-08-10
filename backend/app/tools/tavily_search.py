"""ProjectForge AI — Tavily Web Search Tool.

Used by the Technology Advisor agent for current technology research.
This is NOT RAG — results are passed as context to the LLM, never stored in vector DBs.
"""
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.app.core import settings

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    """A single search result."""
    title: str = ""
    url: str = ""
    content: str = ""


class SearchResults(BaseModel):
    """Collection of search results with availability status."""
    available: bool = True
    results: List[SearchResult] = Field(default_factory=list)
    note: str = ""


class TavilySearchTool:
    """Tavily web search for technology research.

    Used by the Technology Advisor to get current information about technologies.
    Handles missing API key and API failures gracefully.
    """

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self._client = None

    def _get_client(self):
        """Lazy-initialize the Tavily client."""
        if self._client is None:
            if not self.api_key:
                return None
            try:
                from tavily import TavilyClient
                self._client = TavilyClient(api_key=self.api_key)
            except ImportError:
                logger.warning("tavily-python not installed. Web search unavailable.")
                return None
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily client: {e}")
                return None
        return self._client

    def search(self, query: str, max_results: int = 5) -> SearchResults:
        """Perform a web search via Tavily.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            SearchResults with availability flag. Never raises exceptions.
        """
        if not self.api_key:
            return SearchResults(
                available=False,
                note="Tavily API key not configured. Live web research is unavailable. "
                     "Set TAVILY_API_KEY in your .env file to enable web search.",
            )

        client = self._get_client()
        if client is None:
            return SearchResults(
                available=False,
                note="Tavily client could not be initialized. "
                     "Web research is unavailable.",
            )

        try:
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
            )

            results = []
            for item in response.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                ))

            return SearchResults(
                available=True,
                results=results,
                note=f"Found {len(results)} results via Tavily web search.",
            )

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return SearchResults(
                available=False,
                note=f"Tavily search failed: {str(e)}. "
                     "Using LLM's existing knowledge instead.",
            )

    def research_technology(self, technology: str, context: str = "") -> SearchResults:
        """Research a specific technology in context of a project.

        Args:
            technology: Technology name to research.
            context: Project context for more relevant results.

        Returns:
            SearchResults with current technology information.
        """
        query = f"{technology} web development framework 2024 2025 pros cons comparison"
        if context:
            query = f"{technology} for {context} pros cons comparison 2024 2025"
        return self.search(query, max_results=3)

    def compare_technologies(self, technologies: List[str], category: str) -> SearchResults:
        """Compare multiple technologies in a category.

        Args:
            technologies: List of technology names to compare.
            category: Category (e.g., "frontend framework", "database").

        Returns:
            SearchResults with comparison information.
        """
        tech_list = " vs ".join(technologies[:4])  # Limit to avoid too-long queries
        query = f"{tech_list} {category} comparison 2024 2025 which is best"
        return self.search(query, max_results=5)


# Singleton instance
tavily_tool = TavilySearchTool()

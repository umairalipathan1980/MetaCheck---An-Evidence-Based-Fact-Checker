"""
MetaCheck API Clients

External API client classes for fact-checking and Wikipedia.
"""

import os
from typing import List, Optional, Literal, Tuple
import requests
import httpx

from app.core.models import Evidence, SearchStatus


# ============================================================================
# GOOGLE FACT CHECK API CLIENT
# ============================================================================

class GoogleFactCheckClient:
    """Client for Google Fact Check Tools API"""

    def __init__(self):
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self._timeout = 10

    @property
    def api_key(self):
        """Lazy load API key to ensure .env is loaded first"""
        return os.getenv("GOOGLE_FACT_CHECK_API_KEY")

    def search_fact_checks(
        self, query: str, language_code: str = "en", max_results: int = 5
    ) -> Tuple[List[Evidence], SearchStatus]:
        """
        Search for fact-checks related to a query.
        Returns tuple of (evidence_list, status).
        """
        if not self.api_key:
            status = SearchStatus(
                tool="google_fact_check",
                status="no_api_key",
                results_count=0,
                error_message="GOOGLE_FACT_CHECK_API_KEY not configured"
            )
            return [], status

        try:
            params = {
                "query": query,
                "languageCode": language_code,
                "key": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()

            claims = data.get("claims", [])
            evidence_list = []

            for claim in claims[:max_results]:
                review = claim.get("claimReview", [{}])[0]
                publisher = review.get("publisher", {})

                evidence = Evidence(
                    source_name=publisher.get("name", "Unknown Fact-Checker"),
                    source_type="fact_check",
                    url=review.get("url", ""),
                    snippet=f"{claim.get('text', '')[:200]}... Rating: {review.get('textualRating', 'N/A')}",
                    relevance_score=0.9,  # Fact-checks are highly relevant
                    credibility_score=0.95,  # Professional fact-checkers are highly credible
                    stance=self._interpret_rating(review.get("textualRating", ""))
                )
                evidence_list.append(evidence)

            if evidence_list:
                status = SearchStatus(
                    tool="google_fact_check",
                    status="success",
                    results_count=len(evidence_list)
                )
            else:
                status = SearchStatus(
                    tool="google_fact_check",
                    status="no_results",
                    results_count=0
                )

            return evidence_list, status

        except requests.RequestException as e:
            error_msg = str(e)
            print(f"Google Fact Check API error: {error_msg}")
            status = SearchStatus(
                tool="google_fact_check",
                status="error",
                results_count=0,
                error_message=error_msg
            )
            return [], status

    async def search_fact_checks_async(
        self,
        query: str,
        language_code: str = "en",
        max_results: int = 5,
    ) -> Tuple[List[Evidence], SearchStatus]:
        """
        Async search for fact-checks using httpx.
        Returns tuple of (evidence_list, status).
        """
        if not self.api_key:
            status = SearchStatus(
                tool="google_fact_check",
                status="no_api_key",
                results_count=0,
                error_message="GOOGLE_FACT_CHECK_API_KEY not configured"
            )
            return [], status

        try:
            params = {
                "query": query,
                "languageCode": language_code,
                "key": self.api_key,
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            claims = data.get("claims", [])
            evidence_list = []

            for claim in claims[:max_results]:
                review = claim.get("claimReview", [{}])[0]
                publisher = review.get("publisher", {})

                evidence = Evidence(
                    source_name=publisher.get("name", "Unknown Fact-Checker"),
                    source_type="fact_check",
                    url=review.get("url", ""),
                    snippet=f"{claim.get('text', '')[:200]}... Rating: {review.get('textualRating', 'N/A')}",
                    relevance_score=0.9,
                    credibility_score=0.95,
                    stance=self._interpret_rating(review.get("textualRating", ""))
                )
                evidence_list.append(evidence)

            if evidence_list:
                status = SearchStatus(
                    tool="google_fact_check",
                    status="success",
                    results_count=len(evidence_list)
                )
            else:
                status = SearchStatus(
                    tool="google_fact_check",
                    status="no_results",
                    results_count=0
                )

            return evidence_list, status

        except httpx.HTTPError as e:
            error_msg = str(e)
            print(f"Google Fact Check API error (async): {error_msg}")
            status = SearchStatus(
                tool="google_fact_check",
                status="error",
                results_count=0,
                error_message=error_msg
            )
            return [], status

    def _interpret_rating(self, rating: str) -> Literal["supports", "refutes", "neutral", "unclear"]:
        """Interpret fact-checker rating"""
        rating_lower = rating.lower()
        if any(word in rating_lower for word in ["false", "incorrect", "misleading", "pants on fire"]):
            return "refutes"
        elif any(word in rating_lower for word in ["true", "correct", "accurate"]):
            return "supports"
        elif any(word in rating_lower for word in ["mixture", "mixed", "partly"]):
            return "neutral"
        else:
            return "unclear"


# ============================================================================
# WIKIPEDIA API CLIENT
# ============================================================================

class WikipediaClient:
    """Client for Wikipedia REST API"""

    def __init__(self):
        self.search_url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
        self.summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        self._timeout = 10

    @property
    def access_token(self):
        """Lazy load access token to ensure .env is loaded first"""
        return os.getenv("WIKIPEDIA_ACCESS_TOKEN")

    @property
    def headers(self):
        """Build headers with optional auth token"""
        headers = {
            "User-Agent": "MetaCheck/1.0 (Educational Tool)",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def search_pages(self, query: str, limit: int = 5) -> List[dict]:
        """Search Wikipedia pages"""
        try:
            response = requests.get(
                self.search_url,
                params={"q": query, "limit": limit},
                headers=self.headers,
                timeout=self._timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("pages", [])
        except requests.RequestException as e:
            print(f"Wikipedia search error: {e}")
            return []

    def get_summary(self, title: str) -> Optional[dict]:
        """Get page summary"""
        try:
            response = requests.get(
                self.summary_url + requests.utils.quote(title),
                headers=self.headers,
                timeout=self._timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Wikipedia summary error: {e}")
            return None

    def search_for_claim(
        self, claim: str, max_results: int = 3
    ) -> Tuple[List[Evidence], SearchStatus]:
        """
        Search Wikipedia for information related to a claim.
        Returns tuple of (evidence_list, status).
        """
        try:
            pages = self.search_pages(claim, limit=max_results)

            # Check if search itself failed (returned empty due to error)
            if pages is None:
                status = SearchStatus(
                    tool="wikipedia",
                    status="error",
                    results_count=0,
                    error_message="Wikipedia search failed"
                )
                return [], status

            evidence_list = []

            for page in pages:
                title = page.get("title", "")
                summary = self.get_summary(title)

                if summary:
                    evidence = Evidence(
                        source_name=f"Wikipedia: {title}",
                        source_type="wikipedia",
                        url=summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        snippet=summary.get("extract", "")[:300],
                        relevance_score=0.7,
                        credibility_score=0.8,  # Wikipedia is generally credible but community-edited
                        stance="neutral"  # Wikipedia aims for neutral POV
                    )
                    evidence_list.append(evidence)

            if evidence_list:
                status = SearchStatus(
                    tool="wikipedia",
                    status="success",
                    results_count=len(evidence_list)
                )
            else:
                status = SearchStatus(
                    tool="wikipedia",
                    status="no_results",
                    results_count=0
                )

            return evidence_list, status

        except Exception as e:
            error_msg = str(e)
            print(f"Wikipedia search_for_claim error: {error_msg}")
            status = SearchStatus(
                tool="wikipedia",
                status="error",
                results_count=0,
                error_message=error_msg
            )
            return [], status

    async def search_pages_async(self, query: str, limit: int = 5) -> List[dict]:
        """Async Wikipedia search."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    self.search_url,
                    params={"q": query, "limit": limit},
                    headers=self.headers,
                )
            response.raise_for_status()
            data = response.json()
            return data.get("pages", [])
        except httpx.HTTPError as e:
            print(f"Wikipedia search error (async): {e}")
            return []

    async def get_summary_async(self, title: str) -> Optional[dict]:
        """Async page summary."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    self.summary_url + requests.utils.quote(title),
                    headers=self.headers,
                )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Wikipedia summary error (async): {e}")
            return None

    async def search_for_claim_async(
        self, claim: str, max_results: int = 3
    ) -> Tuple[List[Evidence], SearchStatus]:
        """Async variant of search_for_claim."""
        try:
            pages = await self.search_pages_async(claim, limit=max_results)

            if pages is None:
                status = SearchStatus(
                    tool="wikipedia",
                    status="error",
                    results_count=0,
                    error_message="Wikipedia search failed"
                )
                return [], status

            evidence_list = []

            for page in pages:
                title = page.get("title", "")
                summary = await self.get_summary_async(title)

                if summary:
                    evidence = Evidence(
                        source_name=f"Wikipedia: {title}",
                        source_type="wikipedia",
                        url=summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        snippet=summary.get("extract", "")[:300],
                        relevance_score=0.7,
                        credibility_score=0.8,
                        stance="neutral"
                    )
                    evidence_list.append(evidence)

            if evidence_list:
                status = SearchStatus(
                    tool="wikipedia",
                    status="success",
                    results_count=len(evidence_list)
                )
            else:
                status = SearchStatus(
                    tool="wikipedia",
                    status="no_results",
                    results_count=0
                )

            return evidence_list, status

        except Exception as e:
            error_msg = str(e)
            print(f"Wikipedia search_for_claim_async error: {error_msg}")
            status = SearchStatus(
                tool="wikipedia",
                status="error",
                results_count=0,
                error_message=error_msg
            )
            return [], status


# ============================================================================
# TAVILY CLIENT (Web Search)
# ============================================================================

class TavilyClient:
    """Client for Tavily Search API - fast web search with relevance scoring"""

    def __init__(self):
        self.base_url = "https://api.tavily.com/search"
        self._timeout = 10

    @property
    def api_key(self):
        """Lazy load API key to ensure .env is loaded first"""
        return os.getenv("TAVILY_API_KEY")

    async def search_async(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic"  # "basic" or "advanced"
    ) -> Tuple[List[Evidence], SearchStatus]:
        """
        Search using Tavily API.

        Args:
            query: Search query (claim text)
            max_results: Max number of results to return
            search_depth: "basic" for faster, "advanced" for more thorough

        Returns:
            Tuple of (evidence_list, status)
        """
        if not self.api_key:
            status = SearchStatus(
                tool="web_search",
                status="no_api_key",
                results_count=0,
                error_message="TAVILY_API_KEY not configured"
            )
            return [], status

        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": False,  # We want raw results, not AI summary
                "include_raw_content": False,  # Save bandwidth
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()

            evidence_list = []
            results = data.get("results", [])

            for result in results:
                # Tavily returns: title, url, content, score (0-1)
                evidence = Evidence(
                    source_name=result.get("title", "Unknown Source"),
                    source_type="web_search",
                    url=result.get("url", ""),
                    snippet=result.get("content", "")[:300],  # Truncate to 300 chars
                    relevance_score=min(1.0, max(0.0, result.get("score", 0.5))),
                    credibility_score=0.7,  # Default for web, will be overridden by domain classification
                    stance="neutral"  # Will be determined by agent
                )
                evidence_list.append(evidence)

            if evidence_list:
                status = SearchStatus(
                    tool="web_search",
                    status="success",
                    results_count=len(evidence_list)
                )
            else:
                status = SearchStatus(
                    tool="web_search",
                    status="no_results",
                    results_count=0
                )

            return evidence_list, status

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {str(e)}"
            print(f"Tavily API error: {error_msg}")
            status = SearchStatus(
                tool="web_search",
                status="error",
                results_count=0,
                error_message=error_msg
            )
            return [], status
        except Exception as e:
            error_msg = str(e)
            print(f"Tavily API error: {error_msg}")
            status = SearchStatus(
                tool="web_search",
                status="error",
                results_count=0,
                error_message=error_msg
            )
            return [], status


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

# Create singleton instances for use throughout the application
google_fact_check_client = GoogleFactCheckClient()
wikipedia_client = WikipediaClient()
tavily_client = TavilyClient()

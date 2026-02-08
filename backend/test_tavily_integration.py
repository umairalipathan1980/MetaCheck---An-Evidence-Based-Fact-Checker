"""
Quick test script for Tavily integration
"""
import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from app.core.clients import tavily_client
from app.core.tools import comprehensive_evidence_tool


async def test_tavily_client():
    """Test TavilyClient directly"""
    print("Testing TavilyClient...")
    evidence, status = await tavily_client.search_async("Eiffel Tower height", max_results=3)

    print(f"Status: {status.status}")
    print(f"Results count: {status.results_count}")
    if status.error_message:
        print(f"Error: {status.error_message}")

    print(f"\nEvidence items: {len(evidence)}")
    for i, ev in enumerate(evidence[:2], 1):
        print(f"{i}. {ev.source_name}")
        print(f"   URL: {ev.url}")
        print(f"   Relevance: {ev.relevance_score}")

    return status.status == "success"


async def test_comprehensive_tool():
    """Test comprehensive_evidence_tool through parallel client calls"""
    print("\n" + "="*60)
    print("Testing parallel evidence gathering (simulating comprehensive_evidence_tool)...")

    from app.core.clients import wikipedia_client, google_fact_check_client

    # Simulate what comprehensive_evidence_tool does: parallel calls
    claim = "Eiffel Tower is 330 meters tall"

    tavily_task = tavily_client.search_async(claim, max_results=3, search_depth="basic")
    wiki_task = wikipedia_client.search_for_claim_async(claim, max_results=2)
    fact_task = google_fact_check_client.search_fact_checks_async(claim, max_results=2)

    (web_evidence, web_status), (wiki_evidence, wiki_status), (fact_evidence, fact_status) = await asyncio.gather(
        tavily_task, wiki_task, fact_task
    )

    print(f"\nSearch statuses:")
    print(f"  Web: {web_status.status} ({web_status.results_count} results)")
    print(f"  Wikipedia: {wiki_status.status} ({wiki_status.results_count} results)")
    print(f"  Fact Check: {fact_status.status} ({fact_status.results_count} results)")

    # Combine evidence
    total_evidence = (web_evidence or []) + (wiki_evidence or []) + (fact_evidence or [])

    print(f"\nTotal evidence items: {len(total_evidence)}")
    print(f"Evidence breakdown:")
    print(f"  Web search: {len(web_evidence or [])}")
    print(f"  Wikipedia: {len(wiki_evidence or [])}")
    print(f"  Fact check: {len(fact_evidence or [])}")

    return len(total_evidence) > 0


async def main():
    print("="*60)
    print("Tavily Integration Test")
    print("="*60)

    # Test 1: TavilyClient
    try:
        tavily_ok = await test_tavily_client()
    except Exception as e:
        print(f"TavilyClient test failed: {e}")
        tavily_ok = False

    # Test 2: Comprehensive tool
    try:
        tool_ok = await test_comprehensive_tool()
    except Exception as e:
        print(f"Comprehensive tool test failed: {e}")
        import traceback
        traceback.print_exc()
        tool_ok = False

    # Summary
    print("\n" + "="*60)
    print("Test Summary:")
    print(f"  TavilyClient: {'PASS' if tavily_ok else 'FAIL'}")
    print(f"  Parallel evidence gathering: {'PASS' if tool_ok else 'FAIL'}")
    print("="*60)

    return tavily_ok and tool_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

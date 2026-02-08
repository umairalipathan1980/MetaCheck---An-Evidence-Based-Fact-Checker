"""
MetaCheck Domain Classification

Fast domain-based credibility assessment using config.json.
"""

import os
import json
from typing import Dict
from urllib.parse import urlparse

from agents import function_tool

from app.core.models import DomainClassification


# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def load_domain_config() -> Dict:
    """Load domain classification config from config.json"""
    # Look for explicit override, then file-local, then CWD
    candidates = []
    env_path = os.getenv("METACHECK_CONFIG_PATH")
    if env_path:
        candidates.append(env_path)

    # Path relative to this file
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Config is in ../config/config.json relative to this file
        candidates.append(os.path.join(base_dir, "..", "config", "config.json"))
        # Also check same directory (for backward compatibility)
        candidates.append(os.path.join(base_dir, "config.json"))
    except Exception:
        pass

    # Fallback to working directory
    candidates.append("config.json")

    for path in candidates:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            continue
        except Exception as exc:
            print(f"Warning: failed to load config from {path}: {exc}")

    print("Warning: config.json not found, using defaults")
    return {"default_score": 0.6, "categories": {}, "resolution_order": []}


# ============================================================================
# DOMAIN CLASSIFICATION
# ============================================================================

def classify_web_source(url: str, title: str = "", snippet: str = "") -> Dict:
    """
    Fast domain-based credibility assessment using config.json.

    Args:
        url: Source URL
        title: Article title (optional, for context)
        snippet: Article snippet (optional, for context)

    Returns:
        {
            'credibility_score': float (0.50-0.85),
            'category': str,
            'description': str,
            'reasoning': str,
            'justification': str,
            'limitations': str
        }
    """
    config = load_domain_config()

    # Parse URL
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
    except Exception:
        # Invalid URL, return default
        return {
            'credibility_score': config.get('default_score', 0.6),
            'category': 'general_web',
            'description': 'General web source (invalid URL)',
            'reasoning': 'Could not parse URL; using default credibility',
            'justification': 'Standard web content with variable editorial oversight',
            'limitations': 'Quality and accuracy varies widely; no systematic fact-checking'
        }

    # Check categories in resolution order
    categories = config.get('categories', {})
    resolution_order = config.get('resolution_order', [])

    for category_key in resolution_order:
        if category_key not in categories:
            continue

        category = categories[category_key]

        # Check domain whitelist (exact match)
        if domain in category.get('domain_whitelist', []):
            return {
                'credibility_score': category['score'],
                'category': category_key,
                'description': category['description'],
                'reasoning': f"Domain '{domain}' identified as {category['description']}",
                'justification': category.get('justification', 'Source matches known credible domain'),
                'limitations': category.get('limitations', 'Assessment based on domain reputation only')
            }

        # Check subdomain suffixes (e.g., .github.io, .wordpress.com)
        subdomain_suffixes = category.get('subdomain_suffixes', [])
        for suffix in subdomain_suffixes:
            if domain.endswith(suffix):
                return {
                    'credibility_score': category['score'],
                    'category': category_key,
                    'description': category['description'],
                    'reasoning': f"Domain '{domain}' matches pattern '{suffix}' for {category['description']}",
                    'justification': category.get('justification', 'Source matches known pattern'),
                    'limitations': category.get('limitations', 'Assessment based on domain pattern only')
                }

        # Check TLD patterns (e.g., .gov, .edu, .ac.uk)
        tld_patterns = category.get('tld_patterns', [])
        for tld in tld_patterns:
            if domain.endswith(tld):
                return {
                    'credibility_score': category['score'],
                    'category': category_key,
                    'description': category['description'],
                    'reasoning': f"Domain '{domain}' has TLD '{tld}' indicating {category['description']}",
                    'justification': category.get('justification', 'TLD indicates institutional source'),
                    'limitations': category.get('limitations', 'Assessment based on domain type only')
                }

    # No match found, use default
    default_score = config.get('default_score', 0.6)
    general_cat = categories.get('general_web', {})

    return {
        'credibility_score': default_score,
        'category': 'general_web',
        'description': general_cat.get('description', 'General web source'),
        'reasoning': f"Domain '{domain}' not recognized; using default credibility assessment",
        'justification': general_cat.get('justification', 'Standard web content with variable editorial oversight'),
        'limitations': general_cat.get('limitations', 'Quality varies widely; no systematic fact-checking; author credentials unknown')
    }


# ============================================================================
# DOMAIN CLASSIFICATION TOOL (for orchestrator)
# ============================================================================

@function_tool
def domain_classification_tool(url: str) -> DomainClassification:
    """
    Classify a web domain's credibility using config.json.

    Args:
        url: The web source URL to classify

    Returns:
        DomainClassification with credibility score and reasoning
    """
    result = classify_web_source(url)
    return DomainClassification(**result)

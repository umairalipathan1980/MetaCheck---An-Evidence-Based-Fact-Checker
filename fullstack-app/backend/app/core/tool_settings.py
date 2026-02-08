import json
import os
from pathlib import Path
from typing import Any


DEFAULT_TOOL_SETTINGS = {
    "verification_scope": {
        "basic": {
            "max_claims_to_verify_per_run": 5,
            "max_claims_to_extract": 10,
            "max_web_sources": 3,
            "max_wikipedia_sources": 2,
            "max_fact_check_sources": 2,
        },
        "comprehensive": {
            "max_claims_to_verify_per_run": 5,
            "max_claims_to_extract": 10,
            "max_web_sources": 5,
            "max_wikipedia_sources": 3,
            "max_fact_check_sources": 3,
        },
    },
    "performance_cost_controls": {
        "model_choice": "gpt-5.1",
        "allowed_models": ["gpt-5.1", "gpt-4.1-mini", "gpt-5-mini"],
        "per_claim_timeout_seconds": 90,
    },
}


def _merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged[key] = _merge_dict(base[key], value)
        else:
            merged[key] = value
    return merged


def get_tool_settings_path() -> Path:
    env_path = os.getenv("METACHECK_TOOL_SETTINGS_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parents[1] / "config" / "settings.json"


def load_tool_settings() -> dict[str, Any]:
    path = get_tool_settings_path()
    try:
        with path.open("r", encoding="utf-8") as f:
            user_settings = json.load(f)
            if isinstance(user_settings, dict):
                return _merge_dict(DEFAULT_TOOL_SETTINGS, user_settings)
    except FileNotFoundError:
        pass
    except Exception as exc:
        print(f"Warning: failed to load tool settings from {path}: {exc}")
    return DEFAULT_TOOL_SETTINGS


def _validate_tool_settings(settings: dict[str, Any]) -> dict[str, Any]:
    verification_scope = settings.get("verification_scope", {})
    basic = verification_scope.get("basic", {})
    comprehensive = verification_scope.get("comprehensive", {})
    perf = settings.get("performance_cost_controls", {})

    def _as_int(value: Any, key: str) -> int:
        try:
            return int(value)
        except Exception as exc:
            raise ValueError(f"{key} must be an integer") from exc

    basic_verify = _as_int(basic.get("max_claims_to_verify_per_run"), "basic.max_claims_to_verify_per_run")
    comp_verify = _as_int(
        comprehensive.get("max_claims_to_verify_per_run"),
        "comprehensive.max_claims_to_verify_per_run",
    )
    basic_extract = _as_int(basic.get("max_claims_to_extract"), "basic.max_claims_to_extract")
    comp_extract = _as_int(
        comprehensive.get("max_claims_to_extract"),
        "comprehensive.max_claims_to_extract",
    )

    # Source limits
    basic_web = _as_int(basic.get("max_web_sources"), "basic.max_web_sources")
    basic_wiki = _as_int(basic.get("max_wikipedia_sources"), "basic.max_wikipedia_sources")
    basic_fact = _as_int(basic.get("max_fact_check_sources"), "basic.max_fact_check_sources")
    comp_web = _as_int(comprehensive.get("max_web_sources"), "comprehensive.max_web_sources")
    comp_wiki = _as_int(comprehensive.get("max_wikipedia_sources"), "comprehensive.max_wikipedia_sources")
    comp_fact = _as_int(comprehensive.get("max_fact_check_sources"), "comprehensive.max_fact_check_sources")

    if not 1 <= basic_verify <= 5:
        raise ValueError("basic.max_claims_to_verify_per_run must be between 1 and 5")
    if not 1 <= comp_verify <= 5:
        raise ValueError("comprehensive.max_claims_to_verify_per_run must be between 1 and 5")
    if not 1 <= basic_extract <= 10:
        raise ValueError("basic.max_claims_to_extract must be between 1 and 10")
    if not 1 <= comp_extract <= 10:
        raise ValueError("comprehensive.max_claims_to_extract must be between 1 and 10")

    # Validate source limits (1-5 for each)
    if not 1 <= basic_web <= 5:
        raise ValueError("basic.max_web_sources must be between 1 and 5")
    if not 1 <= basic_wiki <= 5:
        raise ValueError("basic.max_wikipedia_sources must be between 1 and 5")
    if not 1 <= basic_fact <= 5:
        raise ValueError("basic.max_fact_check_sources must be between 1 and 5")
    if not 1 <= comp_web <= 5:
        raise ValueError("comprehensive.max_web_sources must be between 1 and 5")
    if not 1 <= comp_wiki <= 5:
        raise ValueError("comprehensive.max_wikipedia_sources must be between 1 and 5")
    if not 1 <= comp_fact <= 5:
        raise ValueError("comprehensive.max_fact_check_sources must be between 1 and 5")

    allowed_models = perf.get("allowed_models", DEFAULT_TOOL_SETTINGS["performance_cost_controls"]["allowed_models"])
    if not isinstance(allowed_models, list) or not allowed_models:
        raise ValueError("performance_cost_controls.allowed_models must be a non-empty list")
    model_choice = perf.get("model_choice")
    if model_choice not in allowed_models:
        raise ValueError("performance_cost_controls.model_choice must be one of allowed_models")

    try:
        per_claim_timeout = float(perf.get("per_claim_timeout_seconds"))
    except Exception as exc:
        raise ValueError("performance_cost_controls.per_claim_timeout_seconds must be numeric") from exc
    if per_claim_timeout <= 0:
        raise ValueError("performance_cost_controls.per_claim_timeout_seconds must be > 0")

    return {
        "verification_scope": {
            "basic": {
                "max_claims_to_verify_per_run": basic_verify,
                "max_claims_to_extract": basic_extract,
                "max_web_sources": basic_web,
                "max_wikipedia_sources": basic_wiki,
                "max_fact_check_sources": basic_fact,
            },
            "comprehensive": {
                "max_claims_to_verify_per_run": comp_verify,
                "max_claims_to_extract": comp_extract,
                "max_web_sources": comp_web,
                "max_wikipedia_sources": comp_wiki,
                "max_fact_check_sources": comp_fact,
            },
        },
        "performance_cost_controls": {
            "model_choice": model_choice,
            "allowed_models": allowed_models,
            "per_claim_timeout_seconds": per_claim_timeout,
        },
    }


def save_tool_settings(partial_settings: dict[str, Any]) -> dict[str, Any]:
    merged = _merge_dict(DEFAULT_TOOL_SETTINGS, partial_settings or {})
    validated = _validate_tool_settings(merged)

    path = get_tool_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2)
        f.write("\n")
    return validated

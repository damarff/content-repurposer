"""LLM content generation — transforms articles into platform-specific content."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import yaml

from fetcher import Article

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


class Config:
    """Application configuration loaded from config.yaml."""

    def __init__(self, config_path: str) -> None:
        with open(config_path, "r", encoding="utf-8") as fh:
            raw: Dict[str, Any] = yaml.safe_load(fh)

        self.llm_endpoint: str = raw["llm"]["endpoint"]
        self.llm_model: str = raw["llm"]["model"]
        self.llm_api_key: str = os.path.expandvars(raw["llm"]["api_key"])
        self.llm_temperature: float = raw["llm"]["temperature"]
        self.default_platforms: List[str] = raw["platforms"]["default"]
        self.max_chars: Dict[str, int] = raw["platforms"]["max_chars"]


def load_template(platform: str) -> Dict[str, Any]:
    """Load a platform generation template from the templates directory.

    Args:
        platform: Platform name (e.g. 'twitter', 'linkedin').

    Returns:
        Dict with keys: platform, prompt, character_limit, thread.

    Raises:
        FileNotFoundError: If no template exists for the platform.
    """
    path = os.path.join(TEMPLATES_DIR, f"{platform}.yaml")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No template found for platform '{platform}' at {path}")

    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_prompt(article: Article, template: Dict[str, Any]) -> str:
    """Build the full system + user prompt for the LLM.

    Args:
        article: The article to repurpose.
        template: Loaded platform template dict.

    Returns:
        A combined prompt string suitable for an OpenAI-compatible chat API.
    """
    system_message = template["prompt"]
    char_limit = template.get("character_limit", 1000)

    user_message = (
        f"Here is the article to repurpose.\n\n"
        f"Title: {article.title}\n"
        f"Author: {article.author if article.author else 'Unknown'}\n"
        f"Source: {article.source_url}\n\n"
        f"--- ARTICLE BODY ---\n{article.text_body}\n--- END ---\n\n"
        f"Character limit: {char_limit}. "
        f"Generate the {template['platform']} content now."
    )

    return f"{system_message}\n\n---\n\n{user_message}"


def generate_content(
    article: Article,
    platforms: List[str],
    config: Config,
    *,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Generate platform-optimised content for each requested platform.

    Args:
        article: The article to repurpose.
        platforms: List of platform names (e.g. 'twitter', 'linkedin').
        config: Application configuration.
        dry_run: If True, return placeholder text instead of calling the LLM.

    Returns:
        Dict mapping platform name -> generated content string.

    Raises:
        ValueError: If a platform has no template.
        requests.RequestException: If the LLM API call fails.
    """
    results: Dict[str, str] = {}

    for platform in platforms:
        logger.info("Generating content for platform: %s", platform)
        template = load_template(platform)
        prompt = build_prompt(article, template)

        if dry_run:
            results[platform] = f"[DRY RUN] Would generate {template['platform']} content"
            continue

        content = _call_llm(prompt, config)
        results[platform] = content

    return results


def _call_llm(prompt: str, config: Config) -> str:
    """Call an OpenAI-compatible chat completions API.

    Args:
        prompt: The full prompt string.
        config: App config with endpoint, model, key, temperature.

    Returns:
        The generated text response.
    """
    headers = {
        "Authorization": f"Bearer {config.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": config.llm_temperature,
        "max_tokens": 2048,
    }

    logger.debug("Sending request to %s with model %s", config.llm_endpoint, config.llm_model)

    response = requests.post(
        f"{config.llm_endpoint}/chat/completions",
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content.strip()


def save_output(content: str, platform: str, output_dir: str) -> str:
    """Save generated content to a markdown file.

    Args:
        content: The generated text.
        platform: Platform name used in the filename.
        output_dir: Directory to write into.

    Returns:
        The absolute path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{platform}-{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content)

    logger.info("Saved %s content to %s", platform, filepath)
    return os.path.abspath(filepath)

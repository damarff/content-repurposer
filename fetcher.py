"""Article content fetcher — extracts main content from URLs or reads text files."""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15


@dataclass
class Article:
    """Normalised article representation extracted from a source."""

    title: str = ""
    author: str = ""
    text_body: str = ""
    publish_date: Optional[str] = None
    source_url: str = ""
    raw_html: str = ""


def fetch_article(source: str) -> Article:
    """Fetch article content from a URL or local text file.

    Args:
        source: A URL (http/https) or path to a local text file.

    Returns:
        An Article dataclass with extracted metadata and clean text body.

    Raises:
        FileNotFoundError: If the source is a file path and does not exist.
        ValueError: If the source is empty or unsupported.
        requests.RequestException: If the HTTP request fails.
    """
    if not source or not source.strip():
        raise ValueError("Source must be a non-empty URL or file path.")

    source = source.strip()

    if re.match(r"^https?://", source, re.IGNORECASE):
        return _fetch_from_url(source)
    else:
        return _fetch_from_file(source)


def _fetch_from_url(url: str) -> Article:
    """Fetch and parse article content from a URL."""
    logger.info("Fetching article from URL: %s", url)

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "lxml")

    article = Article(source_url=url, raw_html=html)
    article.title = _extract_title(soup)
    article.author = _extract_author(soup)
    article.publish_date = _extract_date(soup)
    article.text_body = _extract_main_content(soup)

    logger.info("Successfully fetched article: '%s' by %s", article.title, article.author or "unknown")
    return article


def _fetch_from_file(path: str) -> Article:
    """Read article content from a local text file."""
    expanded = os.path.expanduser(path)
    if not os.path.isfile(expanded):
        raise FileNotFoundError(f"File not found: {expanded}")

    logger.info("Reading article from file: %s", expanded)

    with open(expanded, "r", encoding="utf-8") as fh:
        content = fh.read()

    article = Article(text_body=content, source_url=expanded)

    # Try to infer a title from the first non-empty line
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            article.title = stripped[:120]
            break

    logger.info("Read article from file (first line as title): '%s'", article.title)
    return article


def _extract_title(soup: BeautifulSoup) -> str:
    """Extract the page title from meta tags or <title> element."""
    # Open Graph title
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()

    # Twitter card title
    tw = soup.find("meta", attrs={"name": "twitter:title"})
    if tw and tw.get("content"):
        return tw["content"].strip()

    # h1 heading
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    # HTML title tag
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)

    return "Untitled Article"


def _extract_author(soup: BeautifulSoup) -> str:
    """Extract the author name from meta tags or known selectors."""
    # Schema.org author
    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta and author_meta.get("content"):
        return author_meta["content"].strip()

    # Open Graph
    og_author = soup.find("meta", property="article:author")
    if og_author and og_author.get("content"):
        return og_author["content"].strip()

    # Twitter
    tw = soup.find("meta", attrs={"name": "twitter:creator"})
    if tw and tw.get("content"):
        return tw["content"].strip()

    return ""


def _extract_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract publish date from meta tags or known selectors."""
    # Article published time
    for prop in ("article:published_time", "article:modified_time"):
        meta = soup.find("meta", property=prop)
        if meta and meta.get("content"):
            return meta["content"].strip()

    # Schema date
    for name in ("date", "datePublished", "dateModified"):
        meta = soup.find("meta", attrs={"name": name})
        if meta and meta.get("content"):
            return meta["content"].strip()

    return None


# Common selectors for elements to remove from extracted content.
_NOISE_SELECTORS = [
    "nav", "footer", "header", "aside",
    ".nav", ".navbar", ".navigation", ".menu",
    ".sidebar", ".ad", ".ads", ".advertisement",
    ".social-share", ".share-buttons",
    ".comments", ".comment",
    ".related-posts", ".recommended",
    ".cookie", ".popup", ".modal",
    "script", "style", "noscript",
    ".author-bio", ".byline",
]


def _extract_main_content(soup: BeautifulSoup) -> str:
    """Remove noise elements and return clean body text."""
    # Remove unwanted elements
    for selector in _NOISE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    # Try <article> first
    article_tag = soup.find("article")
    if article_tag:
        return _get_clean_text(article_tag)

    # Try <main> or [role="main"]
    main_tag = soup.find("main") or soup.find(attrs={"role": "main"})
    if main_tag:
        return _get_clean_text(main_tag)

    # Fallback: .post-content, .entry-content, .content, #content
    for class_name in (".post-content", ".entry-content", ".content", "#content", ".article-body"):
        container = soup.select_one(class_name)
        if container:
            return _get_clean_text(container)

    # Last resort: <body>
    body = soup.find("body")
    if body:
        return _get_clean_text(body)

    return ""


def _get_clean_text(element: Tag) -> str:
    """Extract clean text from a BeautifulSoup element, normalising whitespace."""
    lines = []
    for child in element.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre"], recursive=True):
        text = child.get_text(strip=True)
        if text:
            lines.append(text)

    return "\n\n".join(lines)

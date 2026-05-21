#!/usr/bin/env python3
"""Content Repurposer CLI — transforms a blog post into multi-platform content."""

import argparse
import logging
import os
import sys

from fetcher import fetch_article
from repurposer import Config, generate_content, load_template, save_output

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(name)s  %(message)s",
)
logger = logging.getLogger("main")


def _resolve_config_path() -> str:
    """Return the path to config.yaml adjacent to this script."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")


def _resolve_output_dir() -> str:
    """Return the output/ directory adjacent to this script, creating it if needed."""
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(d, exist_ok=True)
    return d


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed namespace with source, platforms, dry_run, config.
    """
    parser = argparse.ArgumentParser(
        description="Content Repurposer AI — Turn one article into Twitter threads, "
                    "LinkedIn posts, newsletters, and video scripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --url https://example.com/blog-post\n"
            "  python main.py sample_data/blog-post.txt\n"
            "  python main.py --url https://example.com/post --platforms twitter,linkedin\n"
            "  python main.py sample_data/blog-post.txt --dry-run\n"
        ),
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--url",
        dest="url",
        type=str,
        default=None,
        help="URL of a blog post to repurpose.",
    )
    source_group.add_argument(
        dest="file",
        type=str,
        nargs="?",
        default=None,
        help="Path to a local text file containing the article.",
    )

    parser.add_argument(
        "--platforms",
        type=str,
        default=None,
        help="Comma-separated list of platforms (default: from config).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be generated without calling the LLM API.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.yaml (default: adjacent config.yaml).",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Returns:
        Exit code (0 on success).
    """
    args = parse_args(argv)
    config_path = args.config or _resolve_config_path()
    output_dir = _resolve_output_dir()

    # Load config
    config = Config(config_path)
    logger.info("Loaded config from %s", config_path)

    # Determine source
    source: str = args.url if args.url else args.file  # type: ignore[assignment]
    if not source:
        logger.error("No source provided (use --url <url> or pass a file path).")
        return 1

    # Determine platforms
    if args.platforms:
        platforms = [p.strip().lower() for p in args.platforms.split(",")]
    else:
        platforms = list(config.default_platforms)
    logger.info("Target platforms: %s", ", ".join(platforms))

    # Validate platform templates exist
    for platform in platforms:
        try:
            load_template(platform)
        except FileNotFoundError as exc:
            logger.error("Invalid platform '%s': %s", platform, exc)
            return 1

    # Fetch article
    logger.info("Fetching article from: %s", source)
    try:
        article = fetch_article(source)
    except (FileNotFoundError, ValueError, Exception) as exc:
        logger.error("Failed to fetch article: %s", exc)
        return 1

    logger.info("Article: '%s' by %s", article.title, article.author or "unknown")

    # Generate content
    logger.info(
        "Generating content (dry_run=%s) ...",
        args.dry_run,
    )
    results = generate_content(
        article=article,
        platforms=platforms,
        config=config,
        dry_run=args.dry_run,
    )

    # Save outputs
    saved_paths = []
    for platform, content in results.items():
        path = save_output(content, platform, output_dir)
        saved_paths.append(path)

    # Summary
    print()
    print("=" * 60)
    print("  Content Repurposer — Complete")
    print("=" * 60)
    print(f"  Source:  {source}")
    print(f"  Title:   {article.title}")
    if article.author:
        print(f"  Author:  {article.author}")
    print(f"  Dry run: {args.dry_run}")
    print()
    for path in saved_paths:
        print(f"  ✅ {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Tests for the Content Repurposer tool — 6 test cases with mocked external calls."""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure the project root is on sys.path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import yaml

from fetcher import Article, fetch_article
from repurposer import Config, build_prompt, generate_content, load_template, save_output
from main import parse_args, main


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_sample_article() -> Article:
    return Article(
        title="The Future of AI Automation",
        author="Jane Doe",
        text_body="This is a sample article body about AI automation in business.",
        source_url="https://example.com/ai-automation",
    )


# ---------------------------------------------------------------------------
# Test 1: Load config
# ---------------------------------------------------------------------------

class TestLoadConfig(unittest.TestCase):
    """Test that config.yaml loads and parses correctly."""

    def test_config_loaded(self):
        config_path = os.path.join(PROJECT_ROOT, "config.yaml")
        config = Config(config_path)
        self.assertIn("gpt", config.llm_model.lower())
        self.assertIn("twitter", config.default_platforms)
        self.assertIn("linkedin", config.default_platforms)
        self.assertEqual(config.max_chars["twitter"], 280)
        self.assertEqual(config.max_chars["linkedin"], 3000)
        self.assertEqual(config.max_chars["newsletter"], 3500)
        self.assertEqual(config.max_chars["video"], 1000)


# ---------------------------------------------------------------------------
# Test 2: Parse sample file
# ---------------------------------------------------------------------------

class TestParseSampleFile(unittest.TestCase):
    """Test that fetch_article reads a local text file correctly."""

    def test_read_sample_file(self):
        sample_path = os.path.join(PROJECT_ROOT, "sample_data", "blog-post.txt")
        article = fetch_article(sample_path)
        self.assertIsInstance(article, Article)
        self.assertTrue(len(article.text_body) > 100)
        self.assertIn("AI Automation", article.title)


# ---------------------------------------------------------------------------
# Test 3: Fetch article from URL (mocked)
# ---------------------------------------------------------------------------

class TestFetchFromURL(unittest.TestCase):
    """Test that fetch_article handles a URL properly with mocked requests."""

    @patch("fetcher.requests.get")
    def test_fetch_url_returns_content(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = (
            "<html><head><title>Test Article</title>"
            "<meta name='author' content='Test Author'>"
            "</head><body><article>"
            "<h1>Test Article</h1>"
            "<p>This is the article body text.</p>"
            "</article></body></html>"
        )
        mock_get.return_value = mock_response

        article = fetch_article("https://example.com/test-article")
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.author, "Test Author")
        self.assertIn("article body text", article.text_body)
        self.assertEqual(article.source_url, "https://example.com/test-article")
        mock_get.assert_called_once()


# ---------------------------------------------------------------------------
# Test 4: Load all platform templates
# ---------------------------------------------------------------------------

class TestLoadTemplates(unittest.TestCase):
    """Test that every platform template YAML is loadable."""

    def test_all_templates_exist(self):
        platforms = ["twitter", "linkedin", "newsletter", "video"]
        for plat in platforms:
            template = load_template(plat)
            self.assertIn("platform", template)
            self.assertEqual(template["platform"], plat)
            self.assertIn("prompt", template)
            self.assertIn("character_limit", template)
            self.assertIn("thread", template)
            self.assertIsInstance(template["prompt"], str)
            self.assertGreater(len(template["prompt"]), 20)


# ---------------------------------------------------------------------------
# Test 5: LLM generate returns expected format (mocked)
# ---------------------------------------------------------------------------

class TestGenerateContent(unittest.TestCase):
    """Test that generate_content returns the expected dict format."""

    def setUp(self):
        self.config_path = os.path.join(PROJECT_ROOT, "config.yaml")
        self.config = Config(self.config_path)
        self.article = _make_sample_article()

    @patch("repurposer._call_llm")
    def test_generate_returns_dict(self, mock_call_llm):
        mock_call_llm.return_value = "Generated LinkedIn post content."

        result = generate_content(
            self.article,
            platforms=["linkedin"],
            config=self.config,
        )
        self.assertIn("linkedin", result)
        self.assertEqual(result["linkedin"], "Generated LinkedIn post content.")
        mock_call_llm.assert_called_once()

    def test_build_prompt_includes_article_data(self):
        template = load_template("twitter")
        prompt = build_prompt(self.article, template)
        self.assertIn(self.article.title, prompt)
        self.assertIn(self.article.author, prompt)
        self.assertIn(self.article.text_body, prompt)

    def test_dry_run_skips_llm(self):
        result = generate_content(
            self.article,
            platforms=["twitter", "linkedin"],
            config=self.config,
            dry_run=True,
        )
        self.assertIn("twitter", result)
        self.assertIn("linkedin", result)
        self.assertIn("DRY RUN", result["twitter"])


# ---------------------------------------------------------------------------
# Test 6: Full CLI pipeline with --dry-run
# ---------------------------------------------------------------------------

class TestCLIPipeline(unittest.TestCase):
    """Test the CLI entry point end-to-end with dry-run mode."""

    def test_cli_dry_run(self):
        sample_path = os.path.join(PROJECT_ROOT, "sample_data", "blog-post.txt")
        test_argv = [
            sample_path,
            "--platforms", "twitter,linkedin",
            "--dry-run",
        ]
        exit_code = main(test_argv)
        self.assertEqual(exit_code, 0, "CLI should exit with 0 on success")

    @patch("fetcher.requests.get")
    def test_cli_url_dry_run(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = (
            "<html><head><title>URL Test Article</title></head>"
            "<body><article><p>Test body content.</p></article></body></html>"
        )
        mock_get.return_value = mock_response

        test_argv = [
            "--url", "https://example.com/sample",
            "--platforms", "twitter",
            "--dry-run",
        ]
        exit_code = main(test_argv)
        self.assertEqual(exit_code, 0, "CLI should exit with 0 on success")
        mock_get.assert_called_once()

    def test_parse_args_url(self):
        args = parse_args(["--url", "https://example.com/post"])
        self.assertEqual(args.url, "https://example.com/post")
        self.assertIsNone(args.file)

    def test_parse_args_file(self):
        args = parse_args(["sample_data/blog-post.txt"])
        self.assertEqual(args.file, "sample_data/blog-post.txt")
        self.assertIsNone(args.url)

    def test_save_output_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_output("Hello world", "twitter", tmpdir)
            self.assertTrue(os.path.isfile(path))
            with open(path, "r") as fh:
                self.assertEqual(fh.read(), "Hello world")
            self.assertIn("twitter-", os.path.basename(path))
            self.assertTrue(path.endswith(".md"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)

# Content Repurposer AI

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/status-production-brightgreen" alt="Production Ready">
</p>

> **One article → Twitter thread, LinkedIn post, newsletter & video script — automatically.**

Content Repurposer AI takes a single blog post (URL or text file) and generates four platform-optimised content variants using an LLM: a Twitter thread, a LinkedIn post, a newsletter introduction, and a short-form video script.

---

## How It Works

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌────────────────┐
│   Source      │     │   Content        │     │   LLM Generation  │     │   Output       │
│              │     │   Extraction     │     │                   │     │                │
│  ┌────────┐  │     │  ┌────────────┐  │     │  ┌─────────────┐  │     │  ┌──────────┐  │
│  │  URL   │──┼─────┼─▶│  fetcher   │──┼─────┼─▶│  repurposer │──┼─────┼─▶│  output/ │  │
│  │        │  │     │  │  .py       │  │     │  │  .py        │  │     │  │  *.md    │  │
│  └────────┘  │     │  └────────────┘  │     │  └─────────────┘  │     │  └──────────┘  │
│  ┌────────┐  │     │                  │     │       │           │     │                │
│  │  .txt  │──┼─────┼──────────────────┼─────┼───────┼───────────┼─────┼────────────────┘
│  └────────┘  │     │                  │     │       │           │
└──────────────┘     └──────────────────┘     │  ┌────┴─────┐    │
                                               │  │ templates│    │
                                               │  │  /*.yaml │    │
                                               │  └──────────┘    │
                                               └──────────────────┘
```

1. **Source** — Provide a URL or local text file containing the article
2. **Extract** — `fetcher.py` extracts title, author, body text, and metadata (removes nav/ads/sidebars)
3. **Generate** — `repurposer.py` loads platform-specific templates and sends them to the LLM
4. **Output** — Each platform variant is saved as a timestamped Markdown file in `output/`

---

## Features

- **Multi-source input** — URL (auto-extracted with BeautifulSoup) or plain text file
- **4 platform templates** — Twitter threads, LinkedIn posts, newsletter intros, video scripts
- **LLM-powered** — OpenAI-compatible API (works with any provider: OpenAI, Together, Groq, etc.)
- **Configurable** — YAML config for model, temperature, endpoint, platform list
- **Dry-run mode** — Test the pipeline without consuming API credits
- **Smart content extraction** — Removes navigation, ads, sidebars, and noise from web pages
- **Portfolio-grade output** — Clean, formatted Markdown ready to publish

---

## Quick Start

```bash
# 1. Clone / enter the project directory
cd ~/projects/hermes-business/content-repurposer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
export LLM_API_KEY="sk-your-openai-key-here"

# 4. Run on a blog post URL
python main.py --url https://example.com/blog-post

# 5. Or use the sample file
python main.py sample_data/blog-post.txt

# 6. Run a specific platform
python main.py sample_data/blog-post.txt --platforms twitter,linkedin

# 7. Dry run (no API call)
python main.py sample_data/blog-post.txt --dry-run
```

### Running Tests

```bash
python test.py
```

All tests mock external calls — no API key needed.

---

## Sample Output

Below are examples of what the tool generates from the same article.

### Twitter Thread

```
1/5 🤖 AI automation isn't a luxury anymore — it's a necessity.

Here's why your business needs to automate in 2026 (thread) 🧵

2/5 Layer 1: Task Automation
Tools like Zapier & n8n save teams 12+ hours/week on repetitive tasks.
The ROI is immediate.

3/5 Layer 2: Content Automation
AI scales your thinking. One memo → Twitter thread, LinkedIn post, newsletter, video script.

4/5 Layer 3: Decision Automation
AI agents handling customer triage, inventory, pricing — 40% reduction in support workload.

5/5 The cost of NOT automating is cognitive drain.

What's ONE task you're going to automate this week? 👇

https://example.com/blog-post
```

### LinkedIn Post

**💡 Most founders are confusing activity with progress.**

AI automation isn't about replacing people — it's about freeing them.

Here are 3 layers every business leader needs to understand:

📌 **Task Automation** — Connect your tools. When a lead comes in, your CRM updates,
Slack notifies, and email sends. All automatic. Time saved: 12 hrs/week.

📌 **Content Automation** — Write once, publish everywhere. AI helps you scale
your voice, not replace it. One strategic point reaches Twitter, LinkedIn,
newsletter, and video.

📌 **Decision Automation** — AI agents that triage support, manage inventory,
adjust pricing. One e-commerce team cut support workload by 40%.

👉 The real cost of not automating? Cognitive drain. Every repetitive task
steals attention from creative work.

**What's the first process you'd automate in your business?**

#AIAutomation #Productivity #BusinessGrowth #FutureOfWork
```

### Newsletter Intro

**Subject: The 12-hour shortcut you're not taking**

Hey friend,

Last week I watched a founder spend three hours manually sending invoice reminders.
Three hours. Her business generates over $2M annually.

We've talked about AI automation before, but I want to get specific today — because
the gap between "I know I should automate" and "I actually did it" is where most
opportunity gets lost...

[Quick Insights]
• Task automation saves 10-15 hrs/week on repetitive work
• Content AI multiplies your reach without multiplying your effort
• Decision agents can handle 40% of support tickets autonomously

What do you think? Hit reply and tell me the one task you'd love to automate.

[Read the full article](https://example.com/blog-post)

---

*Join the conversation — share this with a founder who needs to hear it.*
```

### Video Script (60s)

```
[HOOK — 0:00-0:03]
🎬 [Visual: Clock ticking, fast cuts]
"Your team is wasting 12 hours a week — and you're paying for it."

[POINT 1 — 0:04-0:11]
[Visual: Zapier flow animation]
Task automation is the low-hanging fruit. Connect your tools. One form submission
triggers CRM, Slack, and email — all automatic.

[POINT 2 — 0:12-0:19]
[Visual: One document turning into multiple screens]
Content automation scales your thinking. Write once, publish everywhere. AI handles
the volume, you keep the strategy.

[POINT 3 — 0:20-0:27]
[Visual: Chatbot handling tickets]
Decision automation is the game-changer. AI agents triage support, manage inventory.
One brand cut workload by 40%.

[CTA — 0:28-0:35]
[Visual: "Start Now" animation]
One process. Automate it this week. Your future self will thank you.

Like and follow for more AI automation insights.
```

---

## Use Cases

| Use Case | Why It Works |
|---|---|
| **Solo creators** | Turn one blog post into a week of content across all platforms |
| **Marketing teams** | Repurpose pillar content for social, email, and video |
| **Consultants** | Share insights consistently without spending hours writing |
| **Startups** | Maintain thought leadership presence with minimal effort |
| **Agencies** | Scale content production for multiple clients |

---

## Project Structure

```
content-repurposer/
├── main.py                  # CLI entry point
├── fetcher.py               # Article extraction (URL or file)
├── repurposer.py            # LLM generation + config + output
├── config.yaml              # LLM endpoint, model, platform settings
├── requirements.txt         # Python dependencies
├── test.py                  # 6 test cases (mocked network)
├── __init__.py
├── README.md                # This file
│
├── templates/               # Platform-specific generation prompts
│   ├── __init__.py
│   ├── twitter.yaml
│   ├── linkedin.yaml
│   ├── newsletter.yaml
│   └── video.yaml
│
├── sample_data/
│   └── blog-post.txt        # Sample article for testing
│
└── output/                  # Generated content (auto-created)
    └── .gitkeep
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **HTTP** | requests |
| **HTML Parsing** | BeautifulSoup4 + lxml |
| **Config** | PyYAML |
| **LLM API** | OpenAI-compatible (any provider) |
| **Testing** | unittest + unittest.mock |

---

## Configuration

Edit `config.yaml` to customise behaviour:

```yaml
llm:
  endpoint: "https://api.openai.com/v1"    # Any OpenAI-compatible endpoint
  model: "gpt-4o-mini"                     # Model name
  api_key: "${LLM_API_KEY}"                # Env var or literal key
  temperature: 0.7

platforms:
  default: ["twitter", "linkedin", "newsletter", "video"]
  max_chars:
    twitter: 280
    linkedin: 3000
    newsletter: 3500
    video: 1000
```

---

## License

MIT — use freely, build freely.

---

<p align="center">
  Built for <strong>Hermes Agent</strong> — <a href="https://hermes-agent.nousresearch.com">hermes-agent.nousresearch.com</a>
</p>

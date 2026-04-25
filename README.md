# Chart Explainer AI

A multimodal AI app that analyzes any chart or graph and returns structured, analyst-quality insights — powered by Claude's vision capabilities.

## What it does

**Single Chart Analysis** — upload any chart (bar, line, scatter, heatmap, pie, etc.) and get:
- What the chart shows (plain English)
- Key trend with specific values
- Notable detail (outliers, inflection points)
- Business takeaway
- Chart type assessment

**Two-Chart Comparison** — upload two charts and get:
- Individual summaries for each
- Key similarities and differences
- Combined narrative insight
- Recommended conclusion

## Tech Stack

| Component | Tool |
|---|---|
| Vision LLM | Claude claude-sonnet-4-5 (Anthropic) |
| UI | Streamlit |
| Image processing | Pillow |
| Language | Python 3.9+ |

## Setup

### 1. Clone and install

```bash
git clone https://github.com/yourusername/chart-explainer-ai
cd chart-explainer-ai
pip install -r requirements.txt
```

### 2. Set your API key

Get a free API key at [console.anthropic.com](https://console.anthropic.com)

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

### 4. Share publicly (optional)

Add `share=True` in the run config, or deploy free to [Hugging Face Spaces](https://huggingface.co/spaces):
- Create a new Space → select Streamlit
- Upload `app.py` and `requirements.txt`
- Add `ANTHROPIC_API_KEY` as a secret

## Project Structure

```
chart-explainer/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## Skills Demonstrated

- **Multimodal AI** — sending images to a vision LLM and parsing structured outputs
- **Prompt engineering** — structured output templates for consistent, analyst-quality responses
- **Multi-image reasoning** — simultaneous analysis of two images in one API call
- **Python API integration** — Anthropic SDK, base64 encoding, error handling
- **UI/UX** — clean Streamlit interface with tabs, columns, download buttons
- **Production thinking** — session state management, spinner feedback, graceful error handling

## Sample Charts to Try

Any of these work great:
- Screenshots from Google Finance / Yahoo Finance
- Charts from [Our World in Data](https://ourworldindata.org)
- Any Matplotlib/Seaborn plot you generate
- Business dashboards, academic paper figures, news graphics

## Cost

Roughly **$0.01–0.03 per analysis** using Claude claude-sonnet-4-5. A full day of testing costs under $1.

---

Built as a portfolio project demonstrating multimodal GenAI development.

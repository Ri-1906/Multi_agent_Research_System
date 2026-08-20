# 🪶 Research Desk

An autonomous research pipeline that takes a topic, searches the web, reads the most relevant source in depth, drafts a structured report, and then **critiques and revises its own work** until the quality holds up — no human editing required.

Built with [LangChain](https://www.langchain.com/), [Mistral](https://mistral.ai/), and [Tavily](https://tavily.com/), with both a CLI and a styled Streamlit interface.

🔗 **Live demo:** [your-deployed-url-here.streamlit.app](https://your-deployed-url-here.streamlit.app)

---

## ✨ Features

- **Autonomous search agent** — queries the web via Tavily and returns titles, URLs, and snippets.
- **Autonomous reader agent** — picks the most relevant result and scrapes the full page text.
- **Structured report writer** — synthesizes search + scraped content into an Introduction / Key Findings / Conclusion / Sources report.
- **Self-critique loop** — a critic chain scores the report out of 10 with strengths, weaknesses, and a verdict.
- **Automatic revision** — if the score is below 8, the writer revises based on the critic's feedback, up to a configurable number of attempts.
- **Two interfaces** — a plain CLI (`pipeline.py`) and a polished Streamlit UI (`ui.py`) styled as a "field dossier."
- **Downloadable output** — export the final report as a `.txt` file from the UI.

---

## 🧠 How It Works

```
        ┌──────────────┐
 topic  │  Search Agent │  Tavily web search → titles, URLs, snippets
────────▶  (searchAgent) │
        └──────┬────────┘
               │ top results
        ┌──────▼────────┐
        │  Reader Agent  │  picks best URL → scrapes full page text
        │  (readerAgent) │
        └──────┬────────┘
               │ scraped content
        ┌──────▼────────┐
        │ Writer Chain   │  drafts Intro / Key Findings / Conclusion / Sources
        └──────┬────────┘
               │ draft report
        ┌──────▼────────┐
        │ Critic Chain   │  scores report /10, lists strengths & gaps
        └──────┬────────┘
               │ score < 8?
        ┌──────▼────────┐
        │ Revision Chain │──▶ loops back to Critic (up to MAX_REVISIONS)
        └──────┬────────┘
               │ score ≥ 8 or revisions exhausted
        ┌──────▼────────┐
        │ Final Report   │
        └────────────────┘
```

1. **Search** — `searchAgent()` uses the `webSearch` tool (Tavily) to gather recent, reliable sources on the topic.
2. **Read** — `readerAgent()` uses the `scrape` tool to fetch and clean the full text of the most relevant result.
3. **Write** — `writerChain` combines search results + scraped content into a structured first draft.
4. **Critique** — `criticChain` reviews the draft and returns a score out of 10 with specific feedback.
5. **Revise** — `revise_until_good()` loops the writer and critic together: while the score is below 8 and the revision cap hasn't been hit, the report is rewritten based on feedback and re-scored.

---

## 📸 Screenshots

| Input | Final Report |
|---|---|
| ![Research topic input]("C:\Users\riddh\Pictures\Screenshots\Screenshot 2026-08-20 171019.png") | ![Finished report view](<img width="946" height="898" alt="Screenshot 2026-08-20 171120" src="https://github.com/user-attachments/assets/68dd21e2-fe5a-411a-966c-e1be28bb81c6" />)
(<img width="969" height="889" alt="Screenshot 2026-08-20 171131" src="https://github.com/user-attachments/assets/984a666d-dba8-44ac-93b8-172615cbc3f3" />)

) |

<!-- Add more rows/images as needed, e.g. the critic's notes expander or the search/source panels. -->

---

## 📁 Project Structure

| File          | Purpose                                                                 |
|---------------|--------------------------------------------------------------------------|
| `agents.py`   | Defines the LLM, the search/reader agents, and the writer/critic/revision chains, plus the revision loop (`revise_until_good`). |
| `Tools.py`    | Defines the `webSearch` (Tavily) and `scrape` (requests + BeautifulSoup) tools used by the agents. |
| `pipeline.py` | Command-line entry point that runs the full search → read → write → critique pipeline. |
| `ui.py`       | Streamlit front-end ("Research Desk") that runs the same pipeline with live status updates and a styled report view. |

---

## ✅ Prerequisites

- Python 3.10+
- A [Mistral API key](https://console.mistral.ai/)
- A [Tavily API key](https://tavily.com/)

---

## ⚙️ Installation

1. **Clone the project and enter the directory.**

2. **Install dependencies:**

   ```bash
   pip install langchain langchain-mistralai langchain-google-genai google-genai \
               tavily-python beautifulsoup4 requests python-dotenv streamlit
   ```

3. **Create a `.env` file** in the project root with your API keys:

   ```env
   MISTRAL_API_KEY=your_mistral_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

   > `agents.py` also imports `google-genai` / `langchain-google-genai` for an alternative Gemini-based model, but this path is currently commented out and not required to run the app.

---

## 🚀 Usage

### Option 1 — Command line

```bash
python pipeline.py
```

You'll be prompted to enter a topic. Progress (search results, scraped content, drafts, critic feedback, and revisions) is printed to the console, ending with the final report, score, and number of revisions performed.

### Option 2 — Streamlit UI

```bash
streamlit run ui.py
```

Enter a topic, click **Start research**, and watch the pipeline move through search → read → draft → review in real time. The final page shows:

- The polished report, stamped with its critic score and revision count
- An expandable **critic's notes** section
- An expandable **raw search results** section
- An expandable **scraped source content** section
- A **download button** to save the report as `.txt`

---

## 🔧 Configuration

- **`MAX_REVISIONS`** (in `agents.py`) — caps how many writer/critic cycles the revision loop will run (default: `2`). Increase this for more thorough polishing at the cost of more LLM calls.
- **Passing score** — the loop currently stops early once the critic score reaches `8/10` (hardcoded in `revise_until_good`).
- **Model** — the pipeline currently runs on `mistral-small-2506` via `ChatMistralAI`. Swap this out in `agents.py` (e.g. for `ChatGoogleGenerativeAI`) if you'd rather use a different provider.
- **Scrape length** — `scrape()` in `Tools.py` truncates page text to the first 3,000 characters; adjust this if you need deeper content per source.

---

## 📝 Notes & Possible Improvements

- The reader agent currently scrapes only **one** source per run; extending it to read and merge multiple sources would likely improve report depth.
- `scrape()` uses a simple `BeautifulSoup` text extraction — it won't handle JavaScript-rendered pages.
- There are a couple of minor typos in the agent prompts (`"BAsed"`, `"releveant"`) in `pipeline.py` / `ui.py` — cosmetic only, doesn't affect functionality, but worth cleaning up.
- No persistent storage/history — each run is stateless; consider adding a database or file log if you want to keep past reports.

---

## 📄 License

Add your preferred license here (e.g. MIT).

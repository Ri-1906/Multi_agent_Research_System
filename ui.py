import streamlit as st
from agents import searchAgent, readerAgent, writerChain, criticChain, revise_until_good

st.set_page_config(
    page_title="Research Desk",
    page_icon="🪶",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --bg: #1c1c26;
        --surface: #232330;
        --surface-2: #292937;
        --border: #35354280;
        --border-solid: #38384a;
        --text: #e4e1ea;
        --muted: #8f8fa3;
        --sage: #a7c8b9;
        --tan: #d9b98a;
        --mauve: #cbb9dd;
        --rose: #d99a9a;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }

    /* ---- header ---- */
    .eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--tan);
        margin-bottom: 0.5rem;
    }
    .app-title {
        font-family: 'Lora', serif;
        font-size: 2.4rem;
        font-weight: 600;
        color: #f1edf6;
        margin-bottom: 0.35rem;
        letter-spacing: 0.2px;
        line-height: 1.15;
    }
    .app-subtitle {
        color: var(--muted);
        font-size: 0.95rem;
        margin-bottom: 1.4rem;
        max-width: 34rem;
    }
    .header-rule {
        border: none;
        border-top: 1px dashed var(--border-solid);
        margin: 0 0 1.8rem 0;
    }

    /* ---- text input ---- */
    .stTextInput input {
        background-color: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.65rem 0.85rem;
        font-size: 0.98rem;
    }
    .stTextInput input:focus {
        border: 1px solid var(--sage);
        box-shadow: 0 0 0 1px var(--sage);
    }

    /* ---- primary button ---- */
    .stButton button {
        background-color: var(--sage);
        color: #16211c;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.4rem;
        font-weight: 600;
        font-size: 0.92rem;
        transition: background-color 0.15s ease;
    }
    .stButton button:hover {
        background-color: #bcd8cb;
        color: #16211c;
    }

    /* ---- download / secondary button ---- */
    .stDownloadButton button {
        background-color: transparent;
        color: var(--text);
        border: 1px solid var(--border-solid);
        border-radius: 8px;
        padding: 0.45rem 1.2rem;
        font-weight: 500;
        font-size: 0.88rem;
    }
    .stDownloadButton button:hover {
        border-color: var(--sage);
        color: var(--sage);
    }

    /* ---- report card ---- */
    .report-card {
        background-color: var(--surface);
        border: 1px solid var(--border-solid);
        border-left: 3px solid var(--sage);
        border-radius: 10px;
        padding: 1.6rem 1.8rem 0.4rem 1.8rem;
        margin-bottom: 0.6rem;
    }
    .report-card .eyebrow { margin-bottom: 0.3rem; color: var(--sage); }
    .report-card .report-topic {
        font-family: 'Lora', serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #f1edf6;
        margin-bottom: 0.9rem;
    }
    .report-card .report-body {
        font-family: 'Inter', sans-serif;
        font-size: 0.98rem;
        line-height: 1.65;
    }
    .report-card .report-body h1,
    .report-card .report-body h2,
    .report-card .report-body h3 {
        font-family: 'Lora', serif;
        color: #f1edf6;
    }

    /* meta line under the report, quiet on purpose */
    .report-meta {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: var(--muted);
        letter-spacing: 0.01em;
        margin: 0.2rem 0 1.6rem 0.2rem;
    }
    .report-meta .dot { color: var(--border-solid); margin: 0 0.5rem; }

    /* ---- expander ---- */
    .streamlit-expanderHeader {
        background-color: var(--surface);
        border: 1px solid var(--border-solid);
        border-radius: 8px;
        color: #d5d2de;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
    }
    .streamlit-expanderContent {
        background-color: #201f29;
        border: 1px solid var(--border-solid);
        border-top: none;
        border-radius: 0 0 8px 8px;
    }

    /* status widget text */
    .stStatusWidget-content p {
        color: var(--muted);
    }

    footer, #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Field dossier</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title">Research Desk</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Give it a topic. It searches, reads the most relevant '
    'source, drafts a report, then reviews its own draft until the writing holds up.</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="header-rule">', unsafe_allow_html=True)

topic = st.text_input("Topic", placeholder="e.g. The economics of vertical farming", label_visibility="collapsed")
run_clicked = st.button("Start research")

if "result" not in st.session_state:
    st.session_state.result = None

if run_clicked:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        state = {}
        try:
            with st.status("Searching the web…", expanded=False) as status:
                search = searchAgent()
                search_result = search.invoke({
                    "messages": [("user", f"Find recent, reliable and detailed information about : {topic}")]
                })
                state["search_result"] = search_result["messages"][-1].content
                status.update(label="Search complete", state="complete")

            with st.status("Reading the most relevant source…", expanded=False) as status:
                reader = readerAgent()
                reader_result = reader.invoke({
                    "messages": [("user",
                        f"BAsed on following search results about '{topic}, "
                        f"pick the most releveant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_result'][:800]}"
                    )]
                })
                state["scraped_content"] = reader_result["messages"][-1].content
                status.update(label="Reading complete", state="complete")

            with st.status("Drafting the report…", expanded=False) as status:
                combined_research = (
                    f"Search RESULTS : \n {state['search_result']} \n\n"
                    f"DETAILED SCRAPED CONTENT: \n{state['scraped_content']}\n\n"
                )
                state["report"] = writerChain.invoke({"topic": topic, "research": combined_research})
                status.update(label="Draft ready", state="complete")

            with st.status("Reviewing and polishing…", expanded=False) as status:
                revision_result = revise_until_good(state["report"])
                state["report"] = revision_result["final_report"]
                state["feedback"] = revision_result["final_feedback"]
                state["score"] = revision_result["final_score"]
                state["revisions_performed"] = revision_result["revisions_performed"]
                status.update(label="Review complete", state="complete")

            state["topic"] = topic
            st.session_state.result = state

        except Exception as e:
            st.error(f"Something went wrong while researching this topic: {e}")

result = st.session_state.result

if result:
    st.markdown("<br>", unsafe_allow_html=True)

    # --- report first, nothing above it ---
    st.markdown(
        f'''
        <div class="report-card">
            <div class="eyebrow">Report</div>
            <div class="report-topic">{result.get("topic", "")}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    st.markdown(result["report"])

    revisions = result["revisions_performed"]
    rev_word = "revision" if revisions == 1 else "revisions"
    st.markdown(
        f'''<div class="report-meta">Reviewed to {result["score"]}/10
        <span class="dot">·</span>{revisions} {rev_word}</div>''',
        unsafe_allow_html=True,
    )

    with st.expander("Review — critic's notes"):
        st.markdown(result["feedback"])

    with st.expander("Search — raw results"):
        st.markdown(result["search_result"])

    with st.expander("Source — scraped content"):
        st.markdown(result["scraped_content"])

    st.download_button(
        "Download report as text",
        data=result["report"],
        file_name="research_report.txt",
        mime="text/plain",
    )
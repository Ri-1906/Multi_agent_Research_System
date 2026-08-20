import re
import streamlit as st
from agents import searchAgent, readerAgent, writerChain, criticChain, revise_until_good


def strip_preamble(report_text: str) -> str:
    """Drop leading meta-commentary the writer/critic chain sometimes adds
    (e.g. "Here's the revised report incorporating ... Key improvements
    include: ..."), so only the actual report content is shown/downloaded.
    """
    if not report_text:
        return report_text

    lines = report_text.splitlines()

    for i, line in enumerate(lines):
        if re.match(r"^\s{0,3}#{1,6}\s", line):
            return "\n".join(lines[i:]).strip()

    
    preamble_pattern = re.compile(
        r"^(here'?s|here is|below is|the following is)\b.*\b(report|draft|revision)s?\b",
        re.IGNORECASE,
    )
    if lines and preamble_pattern.search(lines[0].strip()):
        i = 1
        # skip the blank line(s) and any bullet list right after the intro
        while i < len(lines) and (
            not lines[i].strip() or lines[i].lstrip().startswith(("-", "*", "•"))
        ):
            i += 1
        return "\n".join(lines[i:]).strip()

    return report_text.strip()


st.set_page_config(
    page_title="Research Desk",
    page_icon="🪶",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --desk: #1a1924;
        --desk-2: #201f2b;
        --line: #322f42;
        --text-desk: #d9d6e2;
        --muted-desk: #8b87a0;

        --paper: #e8dcc0;
        --paper-shadow: #cdbd94;
        --ink: #2e2515;
        --ink-soft: #5a4f3c;

        --brass: #c99a52;
        --brass-hover: #dbb06c;
        --slate: #8fa7bd;
        --moss: #93ab8a;
        --rose: #c98a86;
    }

    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

    .stApp {
        background-color: var(--desk);
        background-image: repeating-linear-gradient(
            100deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px,
            transparent 1px, transparent 68px
        );
        color: var(--text-desk);
    }

    /* ---------- header ---------- */
    .eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--brass);
        margin-bottom: 0.55rem;
    }
    .app-title {
        font-family: 'Lora', serif;
        font-size: 2.5rem;
        font-weight: 600;
        color: #f4f1fa;
        margin-bottom: 0.4rem;
        line-height: 1.1;
    }
    .app-subtitle {
        color: var(--muted-desk);
        font-size: 0.95rem;
        max-width: 32rem;
        margin-bottom: 1.6rem;
    }
    .header-rule {
        border: none;
        border-top: 1px dashed var(--line);
        margin: 0 0 1.6rem 0;
    }

    /* ---------- inputs ---------- */
    .stTextInput input {
        background-color: var(--desk-2);
        color: var(--text-desk);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
        font-size: 0.98rem;
    }
    .stTextInput input:focus {
        border: 1px solid var(--brass);
        box-shadow: 0 0 0 1px var(--brass);
    }
    .stButton button {
        background-color: var(--brass);
        color: #24190a;
        border: none;
        border-radius: 8px;
        padding: 0.68rem 1.3rem;
        font-weight: 600;
        font-size: 0.92rem;
        width: 100%;
        transition: background-color 0.15s ease;
    }
    .stButton button:hover { background-color: var(--brass-hover); color: #24190a; }

    .stDownloadButton button {
        background-color: transparent;
        color: var(--text-desk);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 500;
        font-size: 0.87rem;
    }
    .stDownloadButton button:hover { border-color: var(--brass); color: var(--brass-hover); }

    /* ---------- the report, styled as a physical page on the desk ---------- */
    .st-key-report-card {
        position: relative;
        background-color: var(--paper);
        border-radius: 3px 14px 3px 3px;
        padding: 2.1rem 2.3rem 2.6rem 2.3rem;
        margin: 0.4rem 0 1.6rem 0;
        box-shadow:
            0 1px 0 var(--paper-shadow) inset,
            0 18px 40px -18px rgba(0,0,0,0.55),
            0 2px 6px rgba(0,0,0,0.25);
    }
    /* folded corner */
    .st-key-report-card::before {
        content: "";
        position: absolute;
        top: 0; right: 0;
        width: 0; height: 0;
        border-style: solid;
        border-width: 0 26px 26px 0;
        border-color: transparent var(--desk) transparent transparent;
        filter: drop-shadow(-2px 2px 3px rgba(0,0,0,0.35));
    }
    .st-key-report-card .eyebrow { color: var(--ink-soft); margin-bottom: 0.3rem; }
    .st-key-report-card .report-topic {
        font-family: 'Lora', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 1.1rem;
        padding-bottom: 0.9rem;
        border-bottom: 1px solid var(--paper-shadow);
    }
    .st-key-report-card div[data-testid="stMarkdownContainer"] {
        font-family: 'Source Serif 4', serif;
        color: var(--ink);
        font-size: 1.02rem;
        line-height: 1.7;
    }
    .st-key-report-card h1, .st-key-report-card h2, .st-key-report-card h3 {
        font-family: 'Lora', serif;
        color: var(--ink);
    }
    .st-key-report-card a { color: #8a5a2a; }

    /* the reviewer's stamp, tucked into the page */
    .stamp {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        color: #7a3530;
        border: 1.5px solid #7a3530;
        border-radius: 4px;
        padding: 0.3rem 0.6rem;
        margin-top: 1.4rem;
        transform: rotate(-2.5deg);
        opacity: 0.82;
    }

    /* ---------- source sections: index cards on the desk, not paper ---------- */
    .st-key-search-section, .st-key-source-section, .st-key-review-section {
        background-color: var(--desk-2);
        border: 1px solid var(--line);
        border-radius: 8px;
        margin-bottom: 0.7rem;
    }
    .st-key-search-section { border-left: 3px solid var(--slate); }
    .st-key-source-section { border-left: 3px solid var(--moss); }
    .st-key-review-section { border-left: 3px solid var(--rose); }

    .streamlit-expanderHeader {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.83rem;
        color: #cfccdb;
        background-color: transparent;
    }
    .streamlit-expanderContent { color: var(--text-desk); }

    .stStatusWidget-content p { color: var(--muted-desk); }

    footer, #MainMenu { visibility: hidden; }
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

col_input, col_btn = st.columns([5, 1.4])
with col_input:
    topic = st.text_input(
        "Topic", placeholder="e.g. The economics of vertical farming", label_visibility="collapsed"
    )
with col_btn:
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
                state["report"] = strip_preamble(revision_result["final_report"])
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

    # --- the report, rendered as one physical page: header + body + stamp all inside it ---
    with st.container(key="report-card"):
        st.markdown('<div class="eyebrow">Report</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-topic">{result.get("topic", "")}</div>', unsafe_allow_html=True)
        st.markdown(result["report"])

        revisions = result["revisions_performed"]
        rev_word = "revision" if revisions == 1 else "revisions"
        st.markdown(
            f'<div class="stamp">REVIEWED · {result["score"]}/10 · {revisions} {rev_word}</div>',
            unsafe_allow_html=True,
        )

    with st.container(key="review-section"):
        with st.expander("Review — critic's notes"):
            st.markdown(result["feedback"])

    with st.container(key="search-section"):
        with st.expander("Search — raw results"):
            st.markdown(result["search_result"])

    with st.container(key="source-section"):
        with st.expander("Source — scraped content"):
            st.markdown(result["scraped_content"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "Download report as text",
        data=result["report"],
        file_name="research_report.txt",
        mime="text/plain",
    )
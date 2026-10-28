import streamlit as st
from router import router
from FAQ import ingest_faq_data, FAQ_chain
from pathlib import Path
from sql import sql_chain

st.set_page_config(
    page_title="ShopMate AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Premium, minimal UI ----------
st.markdown(
    """
    <style>
    :root {
        --ink: #172033;
        --muted: #667085;
        --blue: #315EFB;
        --line: #E7EAF0;
        --surface: #FFFFFF;
        --canvas: #F7F8FC;
        --text-color: #172033;
        --secondary-text-color: #667085;
        --background-color: #F7F8FC;
        --secondary-background-color: #FFFFFF;
    }

    /* Override inherited Streamlit theme colors: the app should stay readable
       even when the user's Streamlit theme is set to dark mode. */
    html, body, [data-testid="stAppViewContainer"], .stApp,
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        background: #F7F8FC !important;
        color: #172033 !important;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
    .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stMarkdownContainer"] p {
        color: #172033;
    }
    .stApp [data-testid="stCaptionContainer"], .stApp small {
        color: #667085 !important;
    }
    [data-testid="stHeader"] { background: rgba(247,248,252,0.96) !important; }
    [data-testid="stToolbar"] { right: 1rem; }
    .block-container {
        max-width: 1000px;
        padding-top: 1.5rem;
        padding-bottom: 7rem;
    }
    #MainMenu, footer { visibility: hidden; }

    .shopmate-brand-row {
        display: flex; align-items: center; gap: 12px;
        padding: 5px 0 18px; border-bottom: 1px solid var(--line);
        margin-bottom: 28px;
    }
    .shopmate-brand-icon {
        width: 44px; height: 44px; display:flex; align-items:center;
        justify-content:center; border-radius: 14px;
        background: #E9EEFF; color: #315EFB; font-size: 22px;
    }
    .shopmate-brand-name {
        display: block; font-size: 1.18rem; font-weight: 750;
        color: #172033 !important; line-height: 1.35; margin: 0;
        padding: 0; text-decoration: none !important;
    }
    .shopmate-brand-sub {
        display: block; color: #667085 !important;
        font-size: .82rem; line-height: 1.5; margin-top: 3px;
    }
    .hero-eyebrow {
        color: #315EFB; font-size: .78rem; font-weight: 750;
        letter-spacing: .11em; text-transform: uppercase; margin-bottom: 8px;
    }
    .hero-title {
        color: #172033; font-size: clamp(2rem, 4vw, 2.8rem);
        font-weight: 780; line-height: 1.1; letter-spacing: -.055em;
        margin: 0 0 10px;
    }
    .hero-copy { color: #667085; font-size: 1rem; line-height: 1.65; max-width: 650px; }
    .section-label {
        font-size: .76rem; color: #778197; font-weight: 750;
        letter-spacing: .09em; text-transform: uppercase; margin: 24px 0 10px;
    }
    .stButton > button {
        width: 100%; min-height: 66px; text-align: left;
        white-space: normal; border: 1px solid #E4E8F1;
        border-radius: 16px; background: #FFFFFF; color: #25304A;
        padding: 13px 16px; box-shadow: 0 2px 8px rgba(25,40,80,.025);
        transition: border .15s ease, background .15s ease, transform .15s ease;
    }
    .stButton > button:hover {
        border-color: #AAB9FF; background: #FDFDFF; color: #244BE8;
        transform: translateY(-1px);
    }
    [data-testid="stChatMessage"] {
        border: 1px solid #E8EBF2; border-radius: 18px;
        background: #FFFFFF !important; padding: 14px 16px; margin-bottom: 12px;
        box-shadow: 0 3px 12px rgba(20,35,70,.025);
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #172033 !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        background: #FFFFFF !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #778197 !important;
        -webkit-text-fill-color: #778197 !important;
        opacity: 1 !important;
    }
    [data-testid="stChatInput"] {
        border: 1px solid #DDE3EF; border-radius: 18px;
        background: #FFFFFF; box-shadow: 0 8px 28px rgba(25,40,80,.07);
    }
    [data-testid="stChatInput"]:focus-within { border-color: #9BAEFF; }
    .route-pill {
        display: inline-block; padding: 4px 9px; margin: 0 0 8px;
        border-radius: 999px; background: #EEF2FF; color: #315EFB;
        font-size: .70rem; font-weight: 750; letter-spacing: .035em;
    }
    .soft-note { color: #8992A5; font-size: .78rem; text-align:center; margin-top: 18px; }

    /* Prevent long ecommerce URLs from stretching the page horizontally. */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] a {
        min-width: 0;
        max-width: 100%;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
    }
    [data-testid="stChatMessage"] a {
        white-space: normal !important;
    }
    [data-testid="stChatMessage"] ol,
    [data-testid="stChatMessage"] ul {
        padding-left: 1.35rem;
        margin-top: .35rem;
    }
    @media (max-width: 640px) {
        .block-container { padding: 1rem 1rem 6rem; }
        .hero-title { font-size: 2rem; }
        .shopmate-brand-row { margin-bottom: 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Keep the existing FAQ ingestion and query routing pipeline.
faqs_path = Path(__file__).parent / "resources" / "faq_data.csv"
ingest_faq_data(faqs_path)


def ask(query):
    route_result = router(query)
    route_name = route_result.name if route_result else "unknown"

    if route_name == "faq":
        response = FAQ_chain(query)
    elif route_name == "sql":
        response = sql_chain(query)
    else:
        response = (
            "I couldn't confidently identify that as a product search or FAQ. "
            "Try asking about a product, price, rating, return, refund, or order policy."
        )
    return response, route_name


# ---------- Header and landing state ----------
st.markdown(
    """
    <div class="shopmate-brand-row">
      <div class="shopmate-brand-icon">✦</div>
      <div class="shopmate-brand-copy">
        <span class="shopmate-brand-name">ShopMate AI</span>
        <span class="shopmate-brand-sub">Your thoughtful shopping companion</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown('<div class="hero-eyebrow">Shopping, made simpler</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">What can I help you<br>find today?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">Discover products, compare ratings, or get quick answers about shopping and store policies — just ask in your own words.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛍️  Find Nike shoes rated above 4.5", key="suggest_product_1"):
            st.session_state.pending_query = "Find Nike shoes with an average rating above 4.5"
            st.rerun()
        if st.button("🏷️  Show products with a discount", key="suggest_product_2"):
            st.session_state.pending_query = "Show me products with more than 30 percent discount"
            st.rerun()
    with col2:
        if st.button("↩️  What is the return policy?", key="suggest_faq_1"):
            st.session_state.pending_query = "What is your return policy?"
            st.rerun()
        if st.button("💳  Which payment methods are accepted?", key="suggest_faq_2"):
            st.session_state.pending_query = "What payment methods are accepted?"
            st.rerun()

    st.markdown(
        '<div class="soft-note">AI-powered answers · Product discovery · FAQ support</div>',
        unsafe_allow_html=True,
    )

# Existing conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and message.get("route"):
            label = {
                "faq": "FAQ ANSWER",
                "sql": "PRODUCT SEARCH",
                "unknown": "ROUTE NOT FOUND",
                "error": "REQUEST ERROR",
            }.get(message["route"], message["route"].upper())
            st.markdown(f'<div class="route-pill">{label}</div>', unsafe_allow_html=True)
        st.markdown(message["content"])

# Clicked prompt takes priority over typed input.
typed_query = st.chat_input("Ask about products, prices, ratings or store policies…")
query = st.session_state.pop("pending_query", None) or typed_query

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Finding the most helpful answer…"):
            try:
                response, route_name = ask(query)
            except Exception as exc:
                # Show a useful local-development message instead of silently
                # disguising every backend error as a routing failure.
                response = (
                    f"Sorry, this request failed with {type(exc).__name__}: {exc}. "
                    "Check the terminal for the full traceback and verify your API "
                    "configuration, model name, database, and dependencies."
                )
                route_name = "error"

        label = {
            "faq": "FAQ ANSWER",
            "sql": "PRODUCT SEARCH",
            "unknown": "ROUTE NOT FOUND",
            "error": "REQUEST ERROR",
        }.get(route_name, route_name.upper())
        st.markdown(f'<div class="route-pill">{label}</div>', unsafe_allow_html=True)
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "route": route_name}
    )
    st.rerun()

if st.session_state.messages:
    if st.button("＋  Start a new conversation", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()

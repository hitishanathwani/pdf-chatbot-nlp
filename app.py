import streamlit as st
from src.chatbot import process_pdfs, get_response
from src.utils import export_chat_history
from datetime import date

st.set_page_config(
    page_title="PDF Chatbot | Hitisha Nathwani",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-header {
        font-size: 2.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4f8ef7, #a855f7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 1rem 0;
    }
    .sub-header { text-align: center; color: #888; margin-bottom: 2rem; }
    .chat-message { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    .user-message { background-color: #1e2530; border-left: 3px solid #4f8ef7; }
    .bot-message { background-color: #161b22; border-left: 3px solid #a855f7; }
    .source-box {
        background-color: #1a1f2e; border: 1px solid #333;
        border-radius: 8px; padding: 0.5rem; margin-top: 0.5rem;
        font-size: 0.85rem; color: #aaa;
    }
    .confidence-high { color: #4ade80; }
    .confidence-mid { color: #facc15; }
    .confidence-low { color: #f87171; }
    .welcome-box {
        background: linear-gradient(135deg, #1e2530, #161b22);
        border: 1px solid #333; border-radius: 16px;
        padding: 2rem; text-align: center; margin: 2rem 0;
    }
    .quote-box {
        background-color: #1a1f2e; border-left: 3px solid #a855f7;
        border-radius: 8px; padding: 1rem 1.5rem;
        margin: 1rem auto; max-width: 600px;
        font-style: italic; color: #ccc; font-size: 0.95rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4f8ef7, #a855f7);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem 1.5rem; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Daily quotes - changes based on date
QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Data is the new oil.", "Clive Humby"),
    ("Without data, you're just another person with an opinion.", "W. Edwards Deming"),
    ("The goal is to turn data into information, and information into insight.", "Carly Fiorina"),
    ("In God we trust. All others must bring data.", "W. Edwards Deming"),
    ("It's not information overload. It's filter failure.", "Clay Shirky"),
    ("The best minds of my generation are thinking about how to make people click ads.", "Jeff Hammerbacher"),
    ("Data really powers everything that we do.", "Jeff Weiner"),
    ("Knowledge is power. Data is the new knowledge.", "Unknown"),
    ("You can have data without information, but you cannot have information without data.", "Daniel Keys Moran"),
    ("What gets measured gets managed.", "Peter Drucker"),
    ("The world is one big data problem.", "Andrew McAfee"),
]

def get_daily_quote():
    day_index = date.today().toordinal() % len(QUOTES)
    return QUOTES[day_index]

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "pdfs_processed" not in st.session_state:
    st.session_state.pdfs_processed = False
if "full_text" not in st.session_state:
    st.session_state.full_text = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "name_submitted" not in st.session_state:
    st.session_state.name_submitted = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# Header
st.markdown('<div class="main-header">🤖 Multi-PDF RAG Chatbot</div>', unsafe_allow_html=True)

# Name collection screen
if not st.session_state.name_submitted:
    quote, author = get_daily_quote()
    st.markdown(f"""
    <div class="welcome-box">
        <h2 style="color:#4f8ef7;">Welcome! 👋</h2>
        <p style="color:#aaa;">Chat with your PDF documents using local AI — 100% private, no data leaves your machine.</p>
        <div class="quote-box">
            "{quote}"<br><br>
            <span style="color:#a855f7;">— {author}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("What's your name?", placeholder="Enter your name to get started...")
        if st.button("Let's Go! 🚀") and name.strip():
            st.session_state.user_name = name.strip()
            st.session_state.name_submitted = True
            st.rerun()
        elif st.button("Skip →"):
            st.session_state.user_name = "there"
            st.session_state.name_submitted = True
            st.rerun()

else:
    # Sidebar
    with st.sidebar:
        quote, author = get_daily_quote()
        st.markdown(f"### 💡 Quote of the Day")
        st.markdown(f'<div class="quote-box">"{quote}" — {author}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📂 Upload PDFs")
        uploaded_files = st.file_uploader(
            "Upload up to 5 PDFs", type="pdf",
            accept_multiple_files=True
        )
        if uploaded_files and len(uploaded_files) > 5:
            st.warning("Maximum 5 PDFs allowed!")
            uploaded_files = uploaded_files[:5]

        if uploaded_files:
            if st.button("🚀 Process PDFs"):
                with st.spinner("Processing PDFs... this may take a minute"):
                    vectorstore, doc_count, chunk_count, full_text = process_pdfs(uploaded_files)
                    if vectorstore:
                        st.session_state.vectorstore = vectorstore
                        st.session_state.pdfs_processed = True
                        st.session_state.full_text = full_text
                        st.session_state.chat_history = []
                        st.success(f"✅ {doc_count} PDF(s) processed into {chunk_count} chunks!")
                    else:
                        st.error("Error processing PDFs. Please try again.")

        st.markdown("---")
        st.markdown("### 📊 Session Stats")
        st.metric("PDFs Loaded", len(uploaded_files) if uploaded_files else 0)
        st.metric("Questions Asked", len(st.session_state.chat_history))

        st.markdown("---")
        if st.session_state.chat_history:
            if st.button("📥 Export Chat History"):
                export_text = export_chat_history(st.session_state.chat_history)
                st.download_button(
                    label="Download Chat",
                    data=export_text,
                    file_name="chat_history.txt",
                    mime="text/plain"
                )
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ How it works")
        st.markdown("""
        1. Upload your PDF files
        2. Click **Process PDFs**
        3. Ask any question!

        Powered by **Llama 3.2** running locally.
        No data leaves your machine. 🔒
        """)

    # Main area
    if not st.session_state.pdfs_processed:
        quote, author = get_daily_quote()
        name = st.session_state.user_name
        st.markdown(f"""
        <div class="welcome-box">
            <h2 style="color:#4f8ef7;">Hi {name}! 👋</h2>
            <p style="color:#aaa; font-size:1.1rem;">Upload a PDF from the sidebar to get started.</p>
            <div class="quote-box">
                "{quote}"<br><br>
                <span style="color:#a855f7;">— {author}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("📂 **Step 1**\nUpload up to 5 PDF files from the sidebar")
        with col2:
            st.info("🚀 **Step 2**\nClick Process PDFs to index your documents")
        with col3:
            st.info("💬 **Step 3**\nAsk any question about your documents")

    else:
        st.markdown(f"### 💬 Chat — Hi {st.session_state.user_name}!")

        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 <b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                confidence = message.get("confidence", 0)
                if confidence > 0.7:
                    conf_class = "confidence-high"
                    conf_label = f"High ({confidence:.0%})"
                elif confidence > 0.4:
                    conf_class = "confidence-mid"
                    conf_label = f"Medium ({confidence:.0%})"
                else:
                    conf_class = "confidence-low"
                    conf_label = f"Low ({confidence:.0%})"

                st.markdown(f'''
                    <div class="chat-message bot-message">
                        🤖 <b>Assistant:</b> {message["content"]}<br><br>
                        <span class="{conf_class}">● Confidence: {conf_label}</span>
                    </div>
                ''', unsafe_allow_html=True)

                if message.get("sources"):
                    with st.expander("📄 View Sources"):
                        for src in message["sources"]:
                            st.markdown(f'<div class="source-box">📄 <b>{src["file"]}</b> — Page {src["page"]}<br><i>{src["preview"]}</i></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Use form so Enter key submits
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_question = st.text_input(
                    "question",
                    label_visibility="collapsed",
                    placeholder=f"Ask a question about your PDFs, {st.session_state.user_name}..."
                )
            with col2:
                submitted = st.form_submit_button("Ask →")

        if submitted and user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.spinner("Thinking..."):
                answer, sources, confidence = get_response(
                    user_question,
                    st.session_state.vectorstore,
                    st.session_state.chat_history,
                    st.session_state.get("full_text", "")
                )
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "confidence": confidence
            })
            st.rerun()
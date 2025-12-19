import streamlit as st
from pathlib import Path
import uuid
import asyncio

from Multi_Modal.main_pdf import get_ans
from conversion import convert_to_pdf
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ==================================================
# 1. SESSION STATE
# ==================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content="You are a helpful AI assistant")
    ]

if "saved_path" not in st.session_state:
    st.session_state.saved_path = None

st.session_state.index_name = "soumyavectorstore"

# ==================================================
# 2. FILE SAVE SETUP
# ==================================================
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_uploaded_file(uploaded_file):
    file_path = UPLOAD_DIR / uploaded_file.name
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path.resolve()
    except Exception as e:
        st.error(f"File save error: {e}")
        return None


# ==================================================
# 3. UI
# ==================================================
st.title("📄 RAG Chatbot")

uploaded_file = st.file_uploader(
    "Upload a document (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"]
)

# ==================================================
# 4. FILE PROCESSING
# ==================================================
if uploaded_file:
    path = save_uploaded_file(uploaded_file)

    if path:
        if path.suffix.lower() == ".pdf":
            final_path = path
        else:
            with st.spinner("Converting to PDF..."):
                try:
                    if asyncio.iscoroutinefunction(convert_to_pdf):
                        final_path = asyncio.run(
                            convert_to_pdf(str(path), str(UPLOAD_DIR))
                        )
                    else:
                        final_path = convert_to_pdf(str(path), str(UPLOAD_DIR))

                    path.unlink()
                except Exception as e:
                    st.error(f"Conversion failed: {e}")
                    st.stop()

        # Reset state for new document
        st.session_state.saved_path = str(final_path)
        st.session_state.chat_history = [
            SystemMessage(content="You are a helpful AI assistant")
        ]

        st.success("✅ File uploaded and indexed!")

# ==================================================
# 5. DISPLAY CHAT HISTORY
# ==================================================
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# ==================================================
# 6. CHAT LOGIC
# ==================================================
user_query = st.chat_input("Ask a question about your document...")

if user_query:
    if not st.session_state.saved_path:
        st.error("⚠️ Please upload a document first.")
        st.stop()

    # User message
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("user"):
        st.write(user_query)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if asyncio.iscoroutinefunction(get_ans):
                    answer = asyncio.run(
                        get_ans(
                            st.session_state.saved_path,
                            user_query,
                            st.session_state.index_name
                        )
                    )
                else:
                    answer = get_ans(
                        st.session_state.saved_path,
                        user_query,
                        st.session_state.index_name
                    )

                answer = str(answer)  # guarantee valid AIMessage content
                st.write(answer)
                st.session_state.chat_history.append(
                    AIMessage(content=answer)
                )

            except Exception as e:
                st.error(f"RAG error: {e}")

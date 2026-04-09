import fitz
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
import tempfile
import os

def extract_full_text(uploaded_files):
    """Extract complete text from all PDFs preserving order"""
    all_texts = []
    all_metadatas = []

    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        doc = fitz.open(tmp_path)
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                all_texts.append(text)
                all_metadatas.append({
                    "file": uploaded_file.name,
                    "page": page_num + 1
                })
        doc.close()
        os.unlink(tmp_path)

    return all_texts, all_metadatas

def process_pdfs(uploaded_files):
    try:
        all_texts, all_metadatas = extract_full_text(uploaded_files)

        # Print extracted text for debugging
        print("EXTRACTED TEXT PREVIEW:")
        for text in all_texts:
            print(text[:200])
            print("---")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=80,
            separators=["\n\n", "\n", ".", " "]
        )

        final_chunks = []
        final_metadatas = []
        for text, meta in zip(all_texts, all_metadatas):
            splits = splitter.split_text(text)
            final_chunks.extend(splits)
            final_metadatas.extend([meta] * len(splits))

        print(f"\nTotal chunks: {len(final_chunks)}")
        print("First 3 chunks:")
        for i, chunk in enumerate(final_chunks[:3]):
            print(f"Chunk {i}: {chunk[:100]}")

        embeddings = OllamaEmbeddings(model="llama3.2")

        vectorstore = Chroma.from_texts(
            texts=final_chunks,
            embedding=embeddings,
            metadatas=final_metadatas
        )

        return vectorstore, len(uploaded_files), len(final_chunks), "\n\n".join(
            [t for t in all_texts]
        )

    except Exception as e:
        print(f"Error processing: {e}")
        return None, 0, 0, ""


def get_response(question, vectorstore, chat_history, full_text=""):
    try:
        history_text = ""
        for msg in chat_history[-4:]:
            role = "Human" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        # Use full document text for better context
        llm = Ollama(model="llama3.2", temperature=0.1)

        prompt = f"""You are a helpful assistant. Answer questions based ONLY on the document content below.
Do not use any outside knowledge. Be precise and read carefully.

FULL DOCUMENT:
{full_text}

Previous conversation:
{history_text}

Question: {question}

Answer based strictly on the document above. If asking about current job, look for the most recent work experience entry."""

        answer = llm.invoke(prompt)

        # Still get sources for display
        docs_with_scores = vectorstore.similarity_search_with_score(question, k=5)
        scores = [score for _, score in docs_with_scores]
        min_score = min(scores) if scores else 7000
        confidence = max(0.1, min(1.0, 1.0 - ((min_score - 5000) / 5000)))

        sources = []
        seen = set()
        for doc, _ in docs_with_scores:
            key = f"{doc.metadata.get('file', 'Unknown')}_{doc.metadata.get('page', 0)}"
            if key not in seen:
                seen.add(key)
                sources.append({
                    "file": doc.metadata.get("file", "Unknown"),
                    "page": doc.metadata.get("page", 0),
                    "preview": doc.page_content[:150] + "..."
                })

        return answer, sources, confidence

    except Exception as e:
        return f"Error: {str(e)}", [], 0
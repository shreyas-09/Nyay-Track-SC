import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

st.markdown("""
<style>
.stButton > button {
    padding: 15px 30px;
    font-size: 20px;
    font-weight: bold;
    background-color: #F16556;
    color: white;
    border: none;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.sidebar.image("lawyer.png")

    st.write("### USER NAME")

    if st.button("📝 New Case"):
        st.switch_page("pages/new_case.py")

    for case in st.session_state.cases:
        st.markdown(f"### {case}")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    st.button("Settings")
    st.button("Help")
    st.button("Logout Account")


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size= 10000, chunk_overlap = 1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_texts(text_chunks, embedding = embeddings)
    vector_store.save_local("faiss_index")


st.title("NEW CASE")

case_name = st.text_input("Enter New Case Diary Number *", "")

pdf_docs = st.file_uploader(
        "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)

if st.button("Process"):
    for pdf in pdf_docs:
        st.session_state.documents.append(pdf.name)
    with st.spinner("Processing"):
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)

        get_vector_store(text_chunks)

    st.success('Processing complete!')
    st.session_state.cases.append(case_name)

    st.switch_page("pages/current_case.py")
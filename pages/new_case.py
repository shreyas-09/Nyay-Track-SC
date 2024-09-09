import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from src.case import Case, insert_case, RelatedCase, insert_related_case, PastJudgment, insert_past_judgment

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


def boostrap_mockup(case_id):
    # Load related cases from files in the "related_cases" folder
    related_case1 = RelatedCase('case1.txt', base_path='../related_cases/')  # Replace with actual file path
    related_case2 = RelatedCase('case2.txt', base_path='../related_cases/')
    related_case3 = RelatedCase('case2.txt', base_path='../related_cases/')
    related_case4 = RelatedCase('case2.txt', base_path='../related_cases/')
    related_case5 = RelatedCase('case5.txt', base_path='../related_cases/')
    related_case6 = RelatedCase('case6.txt', base_path='../related_cases/')
    related_case7 = RelatedCase('case7.txt', base_path='../related_cases/')

    insert_related_case(related_case1, case_id)
    insert_related_case(related_case2, case_id)
    insert_related_case(related_case3, case_id)
    insert_related_case(related_case4, case_id)
    insert_related_case(related_case5, case_id)
    insert_related_case(related_case6, case_id)
    insert_related_case(related_case7, case_id)

    # Load past judgments from files in the "past_judgments" folder
    past_judgment1 = PastJudgment('judgment_file1.txt', base_path='../past_judgments/')  # Replace with actual file path
    past_judgment2 = PastJudgment('judgment_file2.txt', base_path='../past_judgments/')
    past_judgment3 = PastJudgment('judgment_file3.txt', base_path='../past_judgments/')
    past_judgment4 = PastJudgment('judgment_file4.txt', base_path='../past_judgments/')
    past_judgment5 = PastJudgment('judgment_file5.txt', base_path='../past_judgments/')

    insert_past_judgment(past_judgment1, case_id)
    insert_past_judgment(past_judgment2, case_id)
    insert_past_judgment(past_judgment3, case_id)
    insert_past_judgment(past_judgment4, case_id)
    insert_past_judgment(past_judgment5, case_id)


if st.button("Process"):
    for pdf in pdf_docs:
        st.session_state.documents.append(pdf.name)
    with st.spinner("Processing"):
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)

        get_vector_store(text_chunks)
        #TODO: First save and then use case for saving embeddings
        case = Case(case_name, None, raw_text, 1, None)
        case_id = insert_case(case)
        boostrap_mockup(case_id)

    st.success('Processing complete!')
    st.session_state.cases.append(case_name)

    st.switch_page("pages/current_case.py")



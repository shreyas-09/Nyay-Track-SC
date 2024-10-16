import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit_shadcn_ui as ui
from src.case import Case, insert_case, RelatedCase, insert_related_case, PastJudgment, insert_past_judgment, get_cases_by_user_id
from src.case import boot
from components.sidebar import render_sidebar

st.set_page_config(layout="wide")

boot()

st.markdown(
    """
    <style>
        .stProgress > div > div > div > div {
            background-color: green;
        }
    </style>""",
    unsafe_allow_html=True,
)

render_sidebar()

def get_pdf_text(pdf_docs, progress_bar):
    text = ""
    total_pages = sum(len(PdfReader(pdf).pages) for pdf in pdf_docs)
    pages_processed = 0
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
            pages_processed += 1
            progress_bar.progress(pages_processed / total_pages, "Taking text out of documents...")
    return text


def get_text_chunks(text, progress_bar):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    progress_bar.progress(1.0, "Converting text into embeddings...")  # Set progress to 100% when chunking is complete
    return chunks

def get_vector_store(text_chunks, progress_bar):
    embeddings = HuggingFaceEmbeddings()
    total_chunks = len(text_chunks)
    for i, chunk in enumerate(text_chunks):
        FAISS.from_texts([chunk], embedding=embeddings)
        progress_bar.progress((i + 1) / total_chunks, "Saving the data representations in a database...")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


st.title("NEW CASE")

case_name = st.text_input("Enter New Case Diary Number *", "")

pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)


def boostrap_mockup(case_id):
    # Load related cases from files in the "related_cases" folder
    related_case1 = RelatedCase('case1.txt', base_path='related_cases/')  # Replace with actual file path
    related_case2 = RelatedCase('case2.txt', base_path='related_cases/')
    related_case3 = RelatedCase('case2.txt', base_path='related_cases/')
    related_case4 = RelatedCase('case2.txt', base_path='related_cases/')
    related_case5 = RelatedCase('case5.txt', base_path='related_cases/')
    related_case6 = RelatedCase('case6.txt', base_path='related_cases/')
    related_case7 = RelatedCase('case7.txt', base_path='related_cases/')

    insert_related_case(related_case1, case_id)
    insert_related_case(related_case2, case_id)
    insert_related_case(related_case3, case_id)
    insert_related_case(related_case4, case_id)
    insert_related_case(related_case5, case_id)
    insert_related_case(related_case6, case_id)
    insert_related_case(related_case7, case_id)

    # Load past judgments from files in the "past_judgments" folder
    past_judgment1 = PastJudgment('judgment_file1.txt', base_path='past_judgments/')  # Replace with actual file path
    past_judgment2 = PastJudgment('judgment_file2.txt', base_path='past_judgments/')
    past_judgment3 = PastJudgment('judgment_file3.txt', base_path='past_judgments/')
    past_judgment4 = PastJudgment('judgment_file4.txt', base_path='past_judgments/')
    past_judgment5 = PastJudgment('judgment_file5.txt', base_path='past_judgments/')

    insert_past_judgment(past_judgment1, case_id)
    insert_past_judgment(past_judgment2, case_id)
    insert_past_judgment(past_judgment3, case_id)
    insert_past_judgment(past_judgment4, case_id)
    insert_past_judgment(past_judgment5, case_id)

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = ""

if ui.button("Process", className="bg-green-600 text-white", key="btn_process"):
    # for pdf in pdf_docs:
    #     st.session_state.documents.append(pdf.name)

    # st.subheader("Extracting text from documents...")
    extract_progress = st.progress(0, "Taking text out of documents...")
    extract_status = st.empty()
    raw_text = get_pdf_text(pdf_docs, extract_progress)
    # extract_status.success("Text extraction complete!")

    # st.subheader("Converting text into embeddings...")
    chunk_progress = st.progress(0, "Changing the text into data representations...")
    chunk_status = st.empty()
    text_chunks = get_text_chunks(raw_text,chunk_progress)
    # chunk_status.success("Text converted to embeddings!")

    # st.subheader("Storing embeddings into database...")
    data_progress = st.progress(0, "Saving the data representations in a database...")
    data_status = st.empty()
    get_vector_store(text_chunks, data_progress)
    # data_status.success("Data stored!")
    boot()
    #TODO: First save and then use case for saving embeddings
    case = Case(case_name, None, raw_text, 1, None)
    case_id = insert_case(case)
    boostrap_mockup(case_name)

    st.success('Processing complete!')

    st.session_state.current_case_name=case_name

    # st.experimental_set_query_params(case_id=case_name)

    st.switch_page("pages/current_case.py")
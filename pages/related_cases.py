import streamlit as st
import streamlit_shadcn_ui as ui

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings

from src.case import get_cases_by_user_id, get_related_cases, get_past_judgments, get_case_by_name

from src.case import boot
st.set_page_config(layout="wide")

boot()

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name



st.markdown("""
<style>
    .main {
        background-color: #FFFFFF;
    }
    .timeline-container {
        background-color: #FFFFFF;
        position: relative;
        padding-left: 40px;
    }
    .timeline-line {
        position: absolute;
        left: 10px;
        top: 0;
        bottom: 0;
        width: 2px;
        background-color: #4A4A4A;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 20px;timeline-item
    }
    .timeline-dot {
        position: absolute;
        left: -36px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #F0F2F6;
    }
    .timeline-content {
        background-color: #F0F2F6;
        border-radius: 5px;
        padding: 10px 15px;
    }
    .timeline-date {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .timeline-text {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.sidebar.image("lawyer.png")

    if ui.button("📝 New Case", className="bg-red-900 text-white", key="btn_new_case"):
        st.switch_page("pages/new_case.py")

    st.title("Case History")
    boot()
    user_cases = get_cases_by_user_id(1)
    x = 1
    if user_cases:
        for case in user_cases:
            if ui.button(f"📑 {case['case_name']}", className="bg-slate-600 text-white", key = f"ck{x}"):
                st.session_state.current_case_name = case['case_name']
                st.switch_page("pages/current_case.py")
            x+=1
    else:
        print("No cases found for this user.")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    ui.button("Settings ⚙️", className="bg-neutral-500 text-white", size="sm")
    ui.button("Help ❔", className="bg-neutral-500 text-white", size="sm")
    ui.button("Logout 🚪", className="bg-neutral-500 text-white", size="sm")


import os
from dotenv import load_dotenv
def get_conversational_chain():
    prompt_template = """
    Answer the question in as detailed manner as possible from the provided context, make sure to provide all the details, if the answer is not in the provided
    context then just say, "answer is not available in the context", dont provide the wrong answer\n\n
    Context:\n {context}?\n
    Question:\n {question}\n

    Answer:
"""
    ak = ""
    if os.path.isdir("./config"):
        print("local")
        dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
        load_dotenv(dotenv_path)
        ak = os.getenv('api_key')
    else:
        print("Running on Streamlit Cloud")
        ak = st.secrets["api_key"]

    model = ChatGroq(model_name = 'llama-3.1-70b-versatile',api_key = ak)
    
    prompt = PromptTemplate(template= prompt_template,input_variables=["context","question"])
    chain = load_qa_chain(model,chain_type = "stuff",prompt = prompt)
    return chain

def user_input_details(user_question):
    boot()
    case_db = get_case_by_name(st.session_state.current_case_name)
    #if case_db["past_judgment"] == None:
    with st.spinner("Processing"):
            embeddings = HuggingFaceEmbeddings()

            new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)

            chain = get_conversational_chain()


            response = chain(
                {"input_documents":docs, "question": user_question}
                , return_only_outputs=True)

            res = response["output_text"]

            st.markdown(res)



col1, col2, col3 = st.columns(3)
with col1:
    if(ui.button("<< Back to Summary", className="bg-gray-600 text-white", key="btn_sum")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-600 text-white", key="btn_validate_bot_again")):
        st.switch_page("pages/chatbot.py")


st.title("RELATED CASES")

ques = """

You are a legal document expert with the Supreme Court of India. Your task is to analyze the uploaded legal case file and extract similar cases based on the following criteria:

Legal Issues: Identify cases with similar legal issues or points of law.
Facts and Circumstances: Extract cases that share similar facts or circumstances to the current case.
Precedents: Identify any precedent cases cited within the uploaded case and search for additional cases that have referenced similar legal principles.
Court Decisions: Look for similar cases in which the court ruled on issues related to employment, pensionary benefits, or government service status (for instance, if the current case involves employment disputes).
Instructions:
Extract from the Uploaded Case File:

Look for cases that are cited or referred to in the case file. Identify the legal principles or statutes discussed.
If the case references specific laws (e.g., CCS Pension Rules), extract those and identify cases that applied similar laws.
Search the Web for Similar Cases:

Perform an internet search for cases with similar facts and legal principles that might not be directly mentioned in the case file.
Identify cases from the same jurisdiction (Supreme Court of India or relevant High Courts) or related jurisdictions that may have dealt with similar legal questions.
Criteria for Similarity:
Legal Principles: The legal doctrines, laws, or statutes applied in the case.
Facts: Similar circumstances such as employment disputes, pension-related issues, or cases involving the Special Frontier Force (SFF) or government employment status.
Court Rulings: Prior judgments that resulted in decisions on employment status, pensionary benefits, or similar government service issues.
Output Format:
Provide the extracted similar cases in the following structured JSON format:

{
  "similar_cases": [
    {
      "case_name": "Name of the similar case",
      "court": "Court Name",
      "judgment_date": "Judgment Date",
      "case_number": "Case Number (if available)",
      "legal_principle": "A brief description of the legal principle or ruling in this similar case",
      "similarity": "Description of why this case is similar to the current case",
      "source_link": "Link to the case or related resource (if found online)"
    }
  ]
}
Example:
{
  "similar_cases": [
    {
      "case_name": "State of Karnataka v. M.L. Kesari",
      "court": "Supreme Court of India",
      "judgment_date": "2010",
      "case_number": "Civil Appeal No. 7019 of 2010",
      "legal_principle": "Regularization of employees after 10 years of continuous service",
      "similarity": "Addresses the issue of employment regularization, similar to the current case",
      "source_link": "https://www.example.com/case"
    },
    {
      "case_name": "State of Punjab v. Jagjit Singh",
      "court": "Supreme Court of India",
      "judgment_date": "2016",
      "case_number": "Civil Appeal No. 213 of 2016",
      "legal_principle": "Equal pay for equal work for temporary employees",
      "similarity": "Addresses the principle of equal pay for temporary employees, relevant to the current case",
      "source_link": "https://www.example.com/case"
    }
  ]
}
Additional Instructions:
Ensure that all similar cases are related by either fact pattern, legal principles, or court judgments that align with the issues in the current case.
If no similar cases are found in the case file, perform the internet search to fill this gap and return relevant cases. Please give only the JSON code.
"""
user_input_details(ques)


# case_db = get_case_by_name(st.session_state.current_case_name)
# case_id = case_db["case_name"]
# cases = get_past_judgments(case_id)
#
# for case in cases:
#     # st.markdown(case[3])
#     st.markdown(f"""
#     <div class="timeline-item">
#         <div class="timeline-dot"></div>
#         <div class="timeline-content">
#             <div class="timeline-text">{case[3]}</div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)
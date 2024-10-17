import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings
import streamlit_shadcn_ui as ui
from components.sidebar import render_sidebar
from src.case import get_cases_by_user_id, update_defects, get_case_by_name, update_timeline
from src.case import boot
st.set_page_config(page_title="Timeline Of Events", layout="wide")
boot()

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name

col1, col2, col3 = st.columns(3)
# with col1:
#     if(st.button("Check for Defects")):
#         st.switch_page("pages/validate.py")
with col1:
    if(ui.button("<< Back to Summary", className="bg-gray-600 text-white", key="btn_sum_1")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-600 text-white", key="btn_validate_bot_again_1")):
        st.switch_page("pages/chatbot.py")



# st.markdown("<h3>The following timeline of events has been extracted from the files.</h3>", unsafe_allow_html=True)

if "responseSave5" not in st.session_state:
    st.session_state.responseSave5 = ""

render_sidebar()

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
    if case_db["timeline"] == None:
        with st.spinner("Processing"):
            embeddings = HuggingFaceEmbeddings()
            
            new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)

            chain = get_conversational_chain()
            
            response = chain(
                {"input_documents":docs, "question": user_question}
                , return_only_outputs=True)

            res = response["output_text"]

            update_timeline(st.session_state.current_case_name,res)
            return res
    else:
        return case_db["timeline"]

ques = """You are an expert analyst, Compare the files uploaded and extract information to provide the case timelines with date and details in the below format:
"
[
    {
        "date": "January 2008",
        "content": "John Smith employed by Company A as Corporate Title and Executive Vice President for Corporate Subject."
    },
    {
        "date": "2013",
        "content": "Company B contacted Company A regarding a potential collaboration."
    },
    {
        "date": "July 2013",
        "content": "John Smith employed by Company B."
    },
    {
        "date": "December 2013",
        "content": "Smith met with the FDA on behalf of Company B."
    }
]
"
Strictly follow this format and dont include anything else, In the content part of the format provide the details to the corresponding dates.

I repeat strictly follow the above format mentioned inside " " above and give the output in the same format.
"""
text_0 = user_input_details(ques)
# Timeline data
timeline_data = text_0

# Create timeline
st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)


timeline_css = """
<style>
    .timeline {
        position: relative;
        margin: 0 auto;
        padding: 20px 0;
        width: 100%;
    }
    .container {
        padding: 10px 40px;
        position: relative;
        background-color: inherit;
        width: 100%;
    }
    .container::after {
        content: '';
        position: absolute;
        width: 6px;
        background-color: #ccc;
        top: 0;
        bottom: 0;
        left: 30px;
        margin-left: -3px;
    }
    .container.completed::after {
        background-color: #7F1D1D;
    }
    .dot {
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: #bbb;
        border-radius: 50%;
        top: 15px;
        left: 20px;
    }
    .container.completed .dot {
        background-color: #7F1D1D;
    }
    .content {
    padding: 30px; 
    background: #f7f7f7; 
    position: relative;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    border: 1px solid #e0e0e0; 
    transition: transform 0.3s, box-shadow 0.3s; 
}

.content:hover {
    transform: translateY(-2px); /* Slight lift on hover */
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15); /* Enhanced shadow on hover */
}

    .date {
        font-size: 14px;
        color: grey;
    }
</style>
"""


import json
if timeline_data is not None:
    stages = json.loads(timeline_data)
    st.title("Case Timeline")
    st.markdown(timeline_css, unsafe_allow_html=True)

    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    for item in stages:
        st.markdown(f"""
            <div class="container completed">
                <div class="dot"></div>
                <div class="content">
                    <h4>{item["date"]}</h4>
                    <p>{item["content"]}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.write("No timeline data available.")


st.markdown('</div>', unsafe_allow_html=True)




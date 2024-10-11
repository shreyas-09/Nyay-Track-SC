import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings
import streamlit_shadcn_ui as ui

from src.case import get_cases_by_user_id, update_defects, get_case_by_name
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
    # if st.session_state.responseSave5 == "":
    with st.spinner("Processing"):
        embeddings = HuggingFaceEmbeddings()
        
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        
        response = chain(
            {"input_documents":docs, "question": user_question}
            , return_only_outputs=True)

        res = response["output_text"]
        # st.write(res)
        # st.session_state.responseSave5 = res
        return res
    # else:
    #     return st.session_state.responseSave5

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
    padding: 30px; /* Increased padding for more space */
    background: #f7f7f7; /* Light grey background for a softer look */
    position: relative;
    border-radius: 12px; /* Softer corners */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* Enhanced shadow for depth */
    border: 1px solid #e0e0e0; /* Light grey border for definition */
    transition: transform 0.3s, box-shadow 0.3s; /* Smooth transition for hover effect */
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
    # print(timeline_data)
    # # print("&&&&&&&")
    # arr = []
    # s = ""
    # pick = False
    # for i in range(len(timeline_data)):
    #     if timeline_data[i] == '\"':
    #         if pick == False:
    #             pick=True
    #         else:
    #             pick = False
    #             # print(s)
    #             arr.append(s)
    #             s=""
    #     else:
    #         if pick:
    #             s+=timeline_data[i]
    # I = 0
    # while (I+3)<len(arr):
    #     st.markdown(f"""
    #     <div class="timeline-item">
    #         <div class="timeline-dot"></div>
    #         <div class="timeline-content">
    #             <div class="timeline-text">{arr[I+1]}</div>
    #             <div class="timeline-text">{arr[I+3]}</div>
    #         </div>
    #     </div>
    #     """, unsafe_allow_html=True)
    #     I+=4


    stages = json.loads(timeline_data)
    # print(stages)

    # from datetime import datetime

    # # Streamlit layout for timeline component
    st.title("Case Timeline")

    # # Dynamically create the timeline
    # for stage in stages:
        
    #     st.markdown(f"### {stage['date']}")
    #     st.write(f"{stage['content']}")
    #     st.markdown('<hr style="border:1px solid green">', unsafe_allow_html=True)

    st.markdown(timeline_css, unsafe_allow_html=True)

    # Create the timeline
    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    for item in stages:
        # status_class = "completed" if item["complete"] else ""
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




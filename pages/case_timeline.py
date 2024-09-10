import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings
import streamlit_shadcn_ui as ui

from src.case import get_cases_by_user_id, update_defects, get_case_by_name

st.set_page_config(page_title="Timeline Of Events", layout="wide")

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name

col1, col2, col3 = st.columns(3)
# with col1:
#     if(st.button("Check for Defects")):
#         st.switch_page("pages/validate.py")
with col1:
    if(ui.button("<< Back to Summary", className="bg-purple-500 text-white", key="btn_sum_1")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-purple-500 text-white", key="btn_validate_bot_again_1")):
        st.switch_page("pages/chatbot.py")

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

st.markdown("<h3>The following timeline of events has been extracted from the files.</h3>", unsafe_allow_html=True)

if "responseSave5" not in st.session_state:
    st.session_state.responseSave5 = ""

with st.sidebar:
    st.sidebar.image("lawyer.png")

    st.write("### USER NAME")

    if ui.button("📝 New Case", variant="destructive", key="btn_new_case"):
        st.switch_page("pages/new_case.py")

    # for case in st.session_state.cases:
    #     st.markdown(f"### {case}")

    user_cases = get_cases_by_user_id(1)
    if user_cases:
        for case in user_cases:
            print(f"Case ID: {case['id']}, Case Name: {case['case_name']}")
            ui.button(f"📑 {case['case_name']}", variant="outline", key="btn_case")
    else:
        print("No cases found for this user.")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    ui.button("Settings", size="sm")
    ui.button("Help", size="sm")
    ui.button("Logout Account", size="sm")


def get_conversational_chain():
    prompt_template = """
    Answer the question in as detailed manner as possible from the provided context, make sure to provide all the details, if the answer is not in the provided
    context then just say, "answer is not available in the context", dont provide the wrong answer\n\n
    Context:\n {context}?\n
    Question:\n {question}\n

    Answer:
"""
    model = ChatGroq(model_name = 'llama-3.1-70b-versatile',api_key = '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')
    
    prompt = PromptTemplate(template= prompt_template,input_variables=["context","question"])
    chain = load_qa_chain(model,chain_type = "stuff",prompt = prompt)
    return chain

def user_input_details(user_question):
    if st.session_state.responseSave5 == "":
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
            st.session_state.responseSave5 = res
            return res
    else:
        return st.session_state.responseSave5

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

if timeline_data is not None:
    print(timeline_data)
    print("&&&&&&&")
    arr = []
    s = ""
    pick = False
    for i in range(len(timeline_data)):
        if timeline_data[i] == '\"':
            if pick == False:
                pick=True
            else:
                pick = False
                # print(s)
                arr.append(s)
                s=""
        else:
            if pick:
                s+=timeline_data[i]
    I = 0
    while (I+3)<len(arr):
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <div class="timeline-text">{arr[I+1]}</div>
                <div class="timeline-text">{arr[I+3]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        I+=4
else:
    st.write("No timeline data available.")


st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings
import streamlit_shadcn_ui as ui
import os
from dotenv import load_dotenv
from src.case import get_cases_by_user_id, update_defects, get_case_by_name
from src.case import boot
st.set_page_config(layout="wide")
import twilio
from twilio.rest import Client
import requests


boot()

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name

if "responseSave" not in st.session_state:
    st.session_state.responseSave = ""

if "responseSave1" not in st.session_state:
    st.session_state.responseSave1 = ""

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
    if case_db["defects"] == None:
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
           
            update_defects(st.session_state.current_case_name,res)

    else:
        st.markdown(case_db["defects"])
     
def user_input_details_2(user_question):
    boot()
    case_db = get_case_by_name(st.session_state.current_case_name)
    if case_db["defects"] == None:
        with st.spinner("Processing"):
            embeddings = HuggingFaceEmbeddings()
            
            new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)

            chain = get_conversational_chain()

            response_1 = chain(
                {"input_documents":docs, "question": user_question}
                , return_only_outputs=True)

            res = response_1["output_text"]
           
            update_defects(st.session_state.responseSave,res)

    else:
        res = 0.0

    return res

def user_input_details_3(user_question):
    boot()
    case_db = get_case_by_name(st.session_state.current_case_name)

    with st.spinner("Processing"):
        embeddings = HuggingFaceEmbeddings()
            
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        response = chain(
            {"input_documents":docs, "question": user_question}
            , return_only_outputs=True)

        res = response["output_text"]
           
        update_defects(st.session_state.responseSave1,res)

    return res

    
col1, col2, col3 = st.columns(3)

with col1:
    if(ui.button("<< Back to Summary", className="bg-gray-600 text-white", key="btn_sum")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-600 text-white", key="btn_validate_bot_again")):
        st.switch_page("pages/chatbot.py")


st.title("CHECK FOR DEFECTS")

ques = """

You are a legal document analysis expert with the Supreme Court of India. Your task is to evaluate an uploaded legal case file based on the Supreme Court of India 2013 registry rules and identify any procedural defects or issues in the document. 
The defects must be categorized and evaluated according to common filing errors, such as delays, incomplete documentation, incorrect indexing, or improper naming conventions.

Instructions:
Scan the Uploaded Case File:

Review the entire case file to identify and extract specific issues or procedural defects.
Focus on issues commonly raised in the Supreme Court of India’s 2013 rules such as:
Delay in filing or refiling.
Missing or incomplete documents.
Incorrect court fees.
Errors in naming parties.
Vakalatnama issues (e.g., missing signatures, incorrect filing dates).
Incorrect or incomplete indexing.
Inconsistent dates on documents.
Evaluate the Severity of Each Defect:

For each defect identified, rate the severity of the issue on a scale of 1 to 10, where:
1 represents severe issues, such as missing key documents or significant delays.
10 represents no issues or minimal impact on the case.

Ensure the scoring is based on the severity and frequency of the identified issues.

For each case file:

For every defect, provide a clear and well-explained examples from the case file or reference from the case file.
Mention specific page numbers, sections, or references to support your observations.
Add notification date as today’s date for each identified issue.
Output in Table Format:

Return the findings in the following table format:

column 1 as S.No, Column 2 as Category you identify, Column 3 as Details with examples and Column 4 as Notification Date which is todays date and column 5 as the score as calculated above.

Give ONLY the table as the final output
"""

ques_2 = """

You are a legal document analysis expert with the Supreme Court of India. Your task is to evaluate an uploaded legal case file based on the Supreme Court of India 2013 registry rules and identify any procedural defects or issues in the document. 
The defects must be categorized and evaluated according to common filing errors, such as delays, incomplete documentation, incorrect indexing, or improper naming conventions.

Instructions:
Scan the Uploaded Case File:

Review the entire case file to identify and extract specific issues or procedural defects.
Focus on issues commonly raised in the Supreme Court of India’s 2013 rules such as:
Delay in filing or refiling.
Missing or incomplete documents.
Incorrect court fees.
Errors in naming parties.
Vakalatnama issues (e.g., missing signatures, incorrect filing dates).
Incorrect or incomplete indexing.
Inconsistent dates on documents.
Evaluate the Severity of Each Defect:

For each defect identified, rate the severity of the issue on a scale of 1 to 10, where:
1 represents severe issues, such as missing key documents or significant delays.
10 represents no issues or minimal impact on the case.

Ensure the scoring is based on the severity and frequency of the identified issues.

Give the overall score as an output which is average score of each score.

Make sure to give only overall score number in decimals/float as an output and nothing else.

"""

ques_3 = """

You are a legal document analysis expert with the Supreme Court of India. Your task is to evaluate an uploaded legal case file based on the Supreme Court of India 2013 registry rules and identify any procedural defects or issues in the document. 
The defects must be categorized and evaluated according to common filing errors, such as delays, incomplete documentation, incorrect indexing, or improper naming conventions.

Instructions:
Scan the Uploaded Case File:

Review the entire case file to identify and extract specific issues or procedural defects.
Focus on issues commonly raised in the Supreme Court of India’s 2013 rules such as:
Delay in filing or refiling.
Missing or incomplete documents.
Incorrect court fees.
Errors in naming parties.
Vakalatnama issues (e.g., missing signatures, incorrect filing dates).
Incorrect or incomplete indexing.
Inconsistent dates on documents.
Evaluate the Severity of Each Defect:

Give the 50 word summary of the defects in bullet points, Make sure that the summary is 50 words only.

"""

score = user_input_details_2(ques_2)

score = float(score)

score_percentage = (score / 10) * 100

st.subheader("Completion Bar")

custom_css = f"""
<style>
    .progress-bar-container {{
        width: 100%;
        height: 25px;
        background: linear-gradient(to right, #8B1E1E 0.001%, #F6C557 50%, #458D2C 100%);  /* More yellow space */
        border-radius: 15px;
        position: relative;
        box-shadow: none;  /* No glow, more matte */
    }}

    .progress-bar-marker {{
        position: absolute;
        top: 50%;
        left: {score_percentage}%;
        transform: translate(-50%, -50%);
        background-color: black;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 3px solid white;
    }}

    .score-text {{
        position: absolute;
        top: -30px;
        left: {score_percentage}%;
        transform: translateX(-50%);
        font-weight: bold;
        font-size: 14px;
        color: #333;
    }}

    /* Labels for start, middle, and end */
    .progress-label {{
        position: absolute;
        bottom: -20px;
        font-weight: bold;
        font-size: 12px;
        color: #333;
    }}

    .start-label {{
        left: 0;
        transform: translateX(0%);
    }}

    .middle-label {{
        left: 50%;
        transform: translateX(-50%);
    }}

    .end-label {{
        right: 0;
        transform: translateX(0%);
    }}
</style>
"""

# Inject the CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Display the progress bar and marker with percentage above
st.markdown(
    f"""
    <div class="progress-bar-container">
        <div class="score-text">{score_percentage:.1f}%</div>
        <div class="progress-bar-marker"></div>
        <!-- Labels -->
        <div class="progress-label start-label">Poor</div>
        <div class="progress-label middle-label">Good</div>
        <div class="progress-label end-label">Amazing</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

user_input_details(ques)

st.subheader("NOTIFY ABOUT THE INCOMPLETE CLAUSES")

st.write("This will send a report to the advocate via Whatsapp regarding the defects in the documents.")

mobile_number = st.text_input("Advocate's Mobile No. (Extracted via the documents)", "+919591269696")
# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Streamlit UI
#st.title("WhatsApp Chatbot Dashboard")

# Input box to send a message

summary = user_input_details_3(ques_3)
message = "This is the automated bot by the Supreme Court Registry Service to notify you regarding the defects in your file" + st.query_params.case_name+ "This is a summary of defects:" + summary + " Please rectify them at the earliest and upload the documents here"


if ui.button("NOTIFY", className="bg-sky-900 text-white", size="sm", key ="notify"):

    response = client.messages.create(
                body=message,
                from_=WHATSAPP_NUMBER,
                to=TO_NUMBER
            )

    st.success(f"Notification sent to {mobile_number}")

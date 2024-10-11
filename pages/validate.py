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
            # st.markdown(f"""
            #     <div class="timeline-content" style="font-size: 18px;>
            #         <div class="timeline-text">{res}</div>
            #     </div>
            # """, unsafe_allow_html=True)
            # st.session_state.responseSave3 = styled_res
            update_defects(st.session_state.current_case_name,res)
    else:
        st.markdown(case_db["defects"])
        # st.markdown(f"""
        #     <div class="timeline-content" style="font-size: 18px;>
        #         <div class="timeline-text">{case_db["defects"]}</div>
        #     </div>
        # """, unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)
# with col1:
#     if(st.button("Check for Defects")):
#         st.switch_page("pages/validate.py")
with col1:
    if(ui.button("<< Back to Summary", className="bg-gray-600 text-white", key="btn_sum")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-600 text-white", key="btn_validate_bot_again")):
        st.switch_page("pages/chatbot.py")


st.title("CHECK FOR DEFECTS")


score = 7  # Example score out of 10

score_percentage = (score / 10) * 100

st.subheader("Completion Bar")


custom_css = f"""
<style>
    .progress-bar-container {{
        width: 100%;
        height: 25px;
        background: linear-gradient(to right, #D32F2F, #F9A825, #388E3C);
        border-radius: 15px;
        position: relative;
        box-shadow: none;  /* Remove glow effect */
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

ques = """You are an expert lawyer, Compare the files with the  Supreme Court of India registry rules 2013 , Check for all kinds of defects and issues  as stated in the rules and are frequent errors in case filing in the files and highlight in detail with relevant examples from the file where it is not following supreme court rules.

Also give the overall score out of 10 for each category based on severity and amount of issues
Give the results in the form of table with column 1 as S.No, Column 2 as Category you identify  and Column 3 as Details with examples giving all the details about the issue with clear examples from the files where issue is there and Column 4 as Notification Data which is todays date and column 5 as the score as calculated above"""
user_input_details(ques)
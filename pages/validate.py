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

    st.write("### USER NAME")

    if ui.button("📝 New Case", variant="destructive", key="btn_new_case"):
        st.switch_page("pages/new_case.py")

    # for case in st.session_state.cases:
    #     st.markdown(f"### {case}")
    boot()
    user_cases = get_cases_by_user_id(1)
    x = 1
    if user_cases:
        for case in user_cases:
            # print(f"Case ID: {case['id']}, Case Name: {case['case_name']}")
            if ui.button(f"📑 {case['case_name']}", className="bg-gray-500 text-white", key = f"ck{x}"):
                # print("yo")
                st.session_state.current_case_name = case['case_name']
                st.switch_page("pages/current_case.py")
            x+=1
    else:
        print("No cases found for this user.")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    ui.button("Settings ⚙️", className="bg-gray-500 text-white", size="sm")
    ui.button("Help ❔", className="bg-gray-500 text-white", size="sm")
    ui.button("Logout 🚪", className="bg-gray-500 text-white", size="sm")

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
    if(ui.button("<< Back to Summary", className="bg-gray-500 text-white", key="btn_sum")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-500 text-white", key="btn_validate_bot_again")):
        st.switch_page("pages/chatbot.py")


st.title("CHECK FOR DEFECTS")

ques = """You are an expert lawyer, Compare the files with the latest Supreme Court of India rules, Check for issues in below mentioned categories in the files and highlight in detail with relevant examples from the file where it is not following supreme court rules: 1. Pagination Issues 2. Annexure Marking Issues 3. Formatting Issues 4. Blurred Sections
5. Vakalatnama

Also give the overall score out of 10 for each category based on severity and amount of issues
Give the results in the form of table with column 1 as S.No, Column 2 as Category as per above mentioned categories and Column 3 as Details with examples giving all the details about the issue with clear examples from the files where issue is there and Column 4 as Notification Data which is todays date and column 5 as the score as calculated above"""
user_input_details(ques)
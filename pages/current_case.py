import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import streamlit_shadcn_ui as ui

from src.case import get_cases_by_user_id, get_case_by_name, update_processed_output, update_entity_list

from src.case import boot

st.set_page_config(layout="wide")
boot()


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


if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name
# print(st.query_params.case_name)
# print(st.session_state.current_case_name)

if "responseSave3" not in st.session_state:
    st.session_state.responseSave3 = ""

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
            if ui.button(f"📑 {case['case_name']}", className="bg-red-900 text-white", key = f"ck{x}"):
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

def convert_bold_to_html(text):
    parts = text.split("**")
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = f"<strong>{parts[i]}</strong>"
    return "".join(parts)

def convert_bullets_to_html(text):
    lines = text.split("\n") 
    html_lines = []
    in_list = False
    
    for line in lines:
        if line.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            line_content = line[2:] 
            html_lines.append(f"<li>{line_content}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(line)

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)

def user_input_details_1(user_question):
    boot()
    case_db = get_case_by_name(st.session_state.current_case_name)
    if case_db["processed_output"] == None:
        with st.spinner("Processing"):
            embeddings = HuggingFaceEmbeddings()
            
            new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)

            chain = get_conversational_chain()

            
            response = chain(
                {"input_documents":docs, "question": user_question}
                , return_only_outputs=True)

            res = response["output_text"]
            # print(res)
            styled_res = res.replace('\n', '<br>')
            # print(styled_res)
            # styled_res = "**bold hua kya**"+styled_res
            # styled_res = "* point aaya kya"+styled_res
            styled_res = convert_bold_to_html(styled_res)
            styled_res = convert_bullets_to_html(styled_res)

            # TODO: Add processed output to relevant case_id
            #update_processed_output(case_id=None, processed_output=styled_res)
            
            # st.markdown(f"""
            # <div style="font-size: 18px;">
            #     {styled_res}
            # </div>
            # """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="timeline-content" style="font-size: 18px;>
                    <div class="timeline-text">{styled_res}</div>
                </div>
            """, unsafe_allow_html=True)
            # st.session_state.responseSave1 = styled_res
            update_processed_output(st.session_state.current_case_name,styled_res)
    else:
        # st.markdown(f"""
        # <div style="font-size: 18px;">
        #     {case_db["processed_output"]}
        # </div>
        # """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="timeline-content" style="font-size: 18px;>
                <div class="timeline-text">{case_db["processed_output"]}</div>
            </div>
        """, unsafe_allow_html=True)
        

def user_input_details_2(user_question):
    boot()
    case_db = get_case_by_name(st.session_state.current_case_name)
    if case_db["entity_list"] == None:
        with st.spinner("Processing"):
            embeddings = HuggingFaceEmbeddings()
            
            new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)

            chain = get_conversational_chain()

            
            response = chain(
                {"input_documents":docs, "question": user_question}
                , return_only_outputs=True)

            res = response["output_text"]
            # styled_res = res.replace('\n', '<br>')
            styled_res = convert_bold_to_html(res)
            styled_res = convert_bullets_to_html(styled_res)
            # st.write(res)
            st.markdown(f"""
                <div class="timeline-content"; style="font-size: 18px;>
                    <div class="timeline-text">{styled_res}</div>
                </div>
            """, unsafe_allow_html=True)
            # st.session_state.responseSave2 = res
            update_entity_list(st.session_state.current_case_name,styled_res)
    else:
        st.markdown(f"""
            <div class="timeline-content"; style="font-size: 20px;>
                <div class="timeline-text">{case_db["entity_list"]}</div>
            </div>
        """, unsafe_allow_html=True)
        

def user_input_details_3(user_question):
    # if st.session_state.responseSave3 == "":
    with st.spinner("Processing"):
        embeddings = HuggingFaceEmbeddings()
        
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        
        response = chain(
            {"input_documents":docs, "question": user_question}
            , return_only_outputs=True)

        res = response["output_text"]
        st.markdown(f"""
            <div class="timeline-content" style="font-size: 18px;>
                <div class="timeline-text"><strong>{res}</strong></div>
            </div>
        """, unsafe_allow_html=True)
        # st.write(res)
        # st.session_state.responseSave3 = res
    # else:
    #     st.write(st.session_state.responseSave3)


s= "CASE: "+st.session_state.current_case_name

st.title(s)

# st.write("### CHOOSE WHAT TO DO NEXT")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if ui.button("Check for Defects", className="bg-gray-600 text-white", key="btn_validate"):
        st.switch_page("pages/validate.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-600 text-white", key="btn_bot")):
        st.switch_page("pages/chatbot.py")
with col3:
    if(ui.button(f"Timeline of the Case", className="bg-gray-600 text-white", key="btn_time")):
        st.switch_page("pages/case_timeline.py")
with col4:
    if(ui.button("Previous Judgments", className="bg-gray-600 text-white", key="btn_past_judgments")):
        st.switch_page("pages/past_judgments.py")
with col5:
    if ui.button("Related Cases", className="bg-gray-600 text-white", key="btn_related_cases"):
        st.switch_page("pages/related_cases.py")

st.markdown("---")

st.write("### Category of the Case")
ques_0 = """You are an expert lawyer, Based on the files uploaded categorise the case as one of the below mentioned categories:
1. Civil Case
2. Criminal Case
3. Constitutional Case
4. Special Leave Petitions (SLP)
5. Writ Petitions
6. Review & Curative Petitions
7. Advisory Juridictions
8. Election Matters
9. Transfer Petitions
10. Contempt Of Court
11. Service Matters

Give only the name of the category and dont give other information also dont mention the no in start of category.
"""
user_input_details_3(ques_0)

st.markdown("---")

st.write("### Summary of the Case")
ques_1 = "You are an expert lawyer, Give me a brief summary of the files uploaded in 5 bullet points, Use the context from the files and don’t create the context."
user_input_details_1(ques_1)

st.markdown("---")

st.write("### Entity List")
ques_2 = "You are an expert lawyer, Identify the entities in the files uploaded and give the details in a structured table format for each file. Dont mention structured table format in the result"
user_input_details_2(ques_2)

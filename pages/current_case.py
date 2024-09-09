import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

from src.case import get_cases_by_user_id, get_case_by_name, update_processed_output, update_entity_list

st.set_page_config(layout="wide")

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name

if "responseSave3" not in st.session_state:
    st.session_state.responseSave3 = ""


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

    # for case in st.session_state.cases:
    #     st.markdown(f"### {case}")

    user_cases = get_cases_by_user_id(1)
    if user_cases:
        for case in user_cases:
            print(f"Case ID: {case['id']}, Case Name: {case['case_name']}")
            st.button(f"### {case['case_name']}")
    else:
        print("No cases found for this user.")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    st.button("Settings")
    st.button("Help")
    st.button("Logout Account")

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


def user_input_details_1(user_question):
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
        
            styled_res = res.replace('\n', '<br>')

            # TODO: Add processed output to relevant case_id
            #update_processed_output(case_id=None, processed_output=styled_res)

            st.markdown(f"""
            <div style="font-size: 18px;">
                {styled_res}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.responseSave1 = styled_res
            update_processed_output(st.session_state.current_case_name,res)
    else:
        st.markdown(f"""
        <div style="font-size: 18px;">
            {case_db["processed_output"]}
        </div>
        """, unsafe_allow_html=True)

def user_input_details_2(user_question):
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
            st.write(res)
            # st.session_state.responseSave2 = res
            update_entity_list(st.session_state.current_case_name,res)
    else:
        st.write(case_db["entity_list"])

def user_input_details_3(user_question):
    if st.session_state.responseSave3 == "":
        with st.spinner("Processing"):
            embeddings = HuggingFaceEmbeddings()
            
            new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)

            chain = get_conversational_chain()

            
            response = chain(
                {"input_documents":docs, "question": user_question}
                , return_only_outputs=True)

            res = response["output_text"]
            st.write(res)
            st.session_state.responseSave3 = res
    else:
        st.write(st.session_state.responseSave3)


s= "CASE: "+st.session_state.current_case_name

st.title(s)

# st.write("### CHOOSE WHAT TO DO NEXT")
st.write("### CHOOSE WHAT TO DO NEXT")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if(st.button("Check for Defects")):
        st.switch_page("pages/validate.py")
with col2:
    if(st.button("Chat about the Case")):
        st.switch_page("pages/chatbot.py")
with col3:
    if(st.button("Case Documents")):
        st.switch_page("pages/uploaded_docs.py")
with col4:
    if(st.button("Case Timeline")):
        st.switch_page("pages/case_timeline.py")

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

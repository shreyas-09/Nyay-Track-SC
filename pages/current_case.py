import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings

st.set_page_config(layout="wide")

if "responseSave1" not in st.session_state:
    st.session_state.responseSave1 = ""
if "responseSave2" not in st.session_state:
    st.session_state.responseSave2 = ""
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

    for case in st.session_state.cases:
        st.markdown(f"### {case}")
    
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
    if st.session_state.responseSave1 == "":
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
            st.markdown(f"""
            <div style="font-size: 18px;">
                {styled_res}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.responseSave1 = styled_res
    else:
        st.markdown(f"""
        <div style="font-size: 18px;">
            {st.session_state.responseSave1}
        </div>
        """, unsafe_allow_html=True)
        

def user_input_details_2(user_question):
    if st.session_state.responseSave2 == "":
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
            st.markdown(f"""
            <div style="font-size: 18px;">
                {styled_res}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.responseSave2 = styled_res
    else:
        st.markdown(f"""
        <div style="font-size: 18px;">
            {st.session_state.responseSave2}
        </div>
        """, unsafe_allow_html=True)

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

c = st.session_state.cases[-1]
s= "CASE: "+c
st.title(s)

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
user_input_details_1(ques_0)

st.write("### Summary of the Case")
ques_1 = "You are an expert lawyer, Give me a brief summary of the files uploaded in 5 bullet points, Use the context from the files and don’t create the context."
user_input_details_2(ques_1)

st.write("### Entity List")
ques_2 = "You are an expert lawyer, Identify the entities in the files uploaded and give the details in a structured table format for each file. Dont mention structured table format in the result"
user_input_details_3(ques_2)

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
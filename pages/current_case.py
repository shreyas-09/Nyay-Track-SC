import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings

with st.sidebar:
    st.sidebar.image("lawyer.png")

    st.write("### USER NAME")

    if st.button("📝 New Case"):
        st.switch_page("pages/new_case.py")

    for case in st.session_state.cases:
        st.markdown(f"### {case}")
    
    st.text_input("Search Previous Cases")
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


def user_input_details(user_question):
    with st.spinner("Processing"):
        embeddings = HuggingFaceEmbeddings()
        
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        chain = get_conversational_chain()

        
        response = chain(
            {"input_documents":docs, "question": user_question}
            , return_only_outputs=True)

        res = response["output_text"]
        # response = f"Nyay: {res}"
        st.write(res)

st.title("Case Details Page")

st.write("### Summary of the Case")
ques = "You are an expert lawyer, Give me a brief summary of the files uploaded in 5, Use the context from the files and don’t create the context."
user_input_details(ques)

st.title("Entity List")
ques = "You are an expert lawyer, Identify the entities in the files uploaded and give the details in a structured table format for each file."
user_input_details(ques)

st.write("### CHOOSE WHAT TO DO NEXT")
col1, col2, col3 = st.columns(3)
with col1:
    if(st.button("Check for Completeness")):
        st.switch_page("pages/validate.py")
with col2:
    if(st.button("Chat about the Case")):
        st.switch_page("pages/chatbot.py")
with col3:
    if(st.button("Case Documents")):
        st.switch_page("pages/uploaded_docs.py")
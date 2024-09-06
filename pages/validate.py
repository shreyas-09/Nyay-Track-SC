import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings

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

if "responseSave3" not in st.session_state:
    st.session_state.responseSave3 = ""

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


def user_input_details(user_question):
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
        
            styled_res = res.replace('\n', '<br>')
            st.markdown(f"""
            <div style="font-size: 18px;">
                {styled_res}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.responseSave3 = styled_res
    else:
        st.markdown(f"""
        <div style="font-size: 18px;">
            {st.session_state.responseSave3}
        </div>
        """, unsafe_allow_html=True)


st.title("CHECK FOR DEFECTS")

ques = "You are an expert lawyer, Compare the files with the latest Supreme Court of India rules, Point out incompleteness in the documents if any also point out any rules which have not been followed in the files in terms of completeness."
user_input_details(ques)
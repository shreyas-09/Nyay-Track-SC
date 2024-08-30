import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings
from streamlit_extras.app_logo import add_logo

st.markdown("""
    <style>
    
        /* Additional CSS for headings */
        h1 {
            font-size: 30px;
            text-align: center;
            text-transform: uppercase;
        }
    </style>
    """, unsafe_allow_html=True)

# Function to handle navigation by setting query parameters
def navigate_to(page):
    st.query_params["page"]=page
    # st.rerun()

# if "page" not in st.session_state:
#     st.session_state.page = "sign_in"

# # Function to handle page navigation
# def navigate_to(page):
#     st.session_state.page = page


bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size= 10000, chunk_overlap = 1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_texts(text_chunks, embedding = embeddings)
    vector_store.save_local("faiss_index")

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


def user_input(user_question):
    embeddings = HuggingFaceEmbeddings()
    
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    res = response["output_text"]
    response = f"Nyay: {res}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

def user_input_details(user_question):
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

if "cases" not in st.session_state:
    st.session_state.cases = []
if "documents" not in st.session_state:
    st.session_state.documents = []

# Sidebar for navigation
# with st.sidebar:
#     st.image("lawyer.png", width=50)  # Replace with an actual user image
#     st.write("### USER NAME")

#     if st.button("📝 New Case"):
#         navigate_to("new_case")
    
#     # if st.button("📁 Current Case"):
#     #     navigate_to("current_case")
    
#     # st.markdown("### 📁 Previous Cases")
#     for case in cases:
#         st.markdown(f"### {case}")

#     st.text_input("Search Previous Cases")
#     st.button("Settings")
#     st.button("Help")
#     st.button("Logout Account")

# Get the query parameters
query_params = st.query_params
page = query_params.get("page", "sign_in")
## print(page)


# Routing based on the `page` parameter in the URL
if page == "current_case":
    with st.sidebar:
        # st.sidebar.image("lawyer.png", use_column_name = True)  # Replace with an actual user image
        # st.logo("lawyer.png")
        st.sidebar.image("lawyer.png")
        st.write("### USER NAME")

        if st.button("📝 New Case"):
            navigate_to("new_case")
        
        # if st.button("📁 Current Case"):
        #     navigate_to("current_case")
        
        # st.markdown("### 📁 Previous Cases")
        for case in st.session_state.cases:
            st.markdown(f"### {case}")
        # print(st.session_state.cases[0])

        st.text_input("Search Previous Cases")
        st.button("Settings")
        st.button("Help")
        st.button("Logout Account")
    
    st.title("Case Details Page")

    st.write("### Summary of the Case")
    ques = "You are an expert lawyer, Give me a brief summary of the files uploaded in 5, Use the context from the files and don’t create the context."
    user_input_details(ques)

    st.write("### CHOOSE WHAT TO DO NEXT")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if(st.button("Check for Completeness")):
            navigate_to("validate")
    with col2:
        if(st.button("See Entity List")):
            navigate_to("entities")
    with col3:
        if(st.button("Chat about the Case")):
            navigate_to("chatbot")
    with col4:
        if(st.button("Case Documents")):
            navigate_to("uploaded_docs")
    
    # if(st.button("Check for Completeness")):
    #     navigate_to("validate")
    
    # if(st.button("Chat about the Case")):
    #     navigate_to("chatbot")
   
    # if(st.button("Case Documents")):
    #     navigate_to("uploaded_docs")

elif page == "new_case":

    with st.sidebar:
        # st.image("lawyer.png", width=50)  # Replace with an actual user image
        # st.image("lawyer.png", use_column_name = True)
        # st.logo("lawyer.png")
        st.sidebar.image("lawyer.png")
        # add_logo("lawyer.png", height=100) 
        st.write("### USER NAME")

        if st.button("📝 New Case"):
            navigate_to("new_case")
        
        # if st.button("📁 Current Case"):
        #     navigate_to("current_case")
        
        # st.markdown("### 📁 Previous Cases")
        for case in st.session_state.cases:
            st.markdown(f"### {case}")
        

        st.text_input("Search Previous Cases")
        st.button("Settings")
        st.button("Help")
        st.button("Logout Account")

    st.title("NEW CASE")

    # Input for case name
    case_name = st.text_input("Enter New Case Diary Number *", "")

    pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    # print(pdf_docs)
    
    if st.button("Submit"):
        # print(pdf_docs["file_id"])
        for pdf in pdf_docs:
            st.session_state.documents.append(pdf.name)
        with st.spinner("Processing"):
            # Get pdf text
            raw_text = get_pdf_text(pdf_docs)

            # Get the text chunks
            text_chunks = get_text_chunks(raw_text)

            # Create vector store
            get_vector_store(text_chunks)

        st.success('Processing complete!')
        st.session_state.cases.append(case_name)
        
        print(st.session_state.cases[0])
        navigate_to("current_case")
        # navigate_to("current_case")

elif page == "sign_in":
    # Set up the page layout and title
    # st.set_page_config(page_title="Sign In", layout="centered")
    st.image("lawyer.png")
    st.title("Sign In to Your Account")

    # Placeholder for the login status
    login_status = st.empty()

    # Create a sign-in form
    with st.form(key='signin_form'):
        username = st.text_input("Username","user")
        password = st.text_input("Password", "password",type='password')
        
        # Submit button for the form
        submit_button = st.form_submit_button(label="Sign In")

    # Dummy credentials for demonstration purposes
    valid_username = "user"
    valid_password = "password"

    # Check the credentials when the form is submitted
    if submit_button:
        if username == valid_username and password == valid_password:
            login_status.success("Logged in successfully!")
            
            # Redirect to a different page or show content for logged-in users
            navigate_to("new_case")
            # Here, you could use st.experimental_set_query_params or other logic to navigate to another page.
            
        else:
            login_status.error("Invalid username or password")

    # Add a link to reset password or sign up (optional)
    st.write("Forgot your password? [Reset it here](#)")
    st.write("Don't have an account? [Sign up](#)")

elif page == "validate":
    with st.sidebar:
        st.sidebar.image("lawyer.png")# Replace with an actual user image
        st.write("### USER NAME")

        if st.button("📝 New Case"):
            navigate_to("new_case")
        
        # if st.button("📁 Current Case"):
        #     navigate_to("current_case")
        
        # st.markdown("### 📁 Previous Cases")
        for case in st.session_state.cases:
            st.markdown(f"### {case}")
        # print(st.session_state.cases[0])

        st.text_input("Search Previous Cases")
        st.button("Settings")
        st.button("Help")
        st.button("Logout Account")
    
    st.title("CHECK FOR COMPLETENESS")

    # Details Section
    # st.subheader("DETAILS")

    # st.write("**NAME:** ABCD EFGH")
    # st.write("**DATE OF FILING:** 21 Aug 2024")
    # st.write("**Petitioner's Address:** Flat No. 202, Shanti Apartments, Mumbai, Maharashtra - 400069")
    # st.write("**COURT:** Supreme Court")

    ques = "You are an expert lawyer, Compare the files with the latest Supreme Court of India rules, Point out incompleteness in the documents if any also point out any rules which have not been followed in the files in terms of completeness."
    user_input_details(ques)

    # Checklist Section
    # st.subheader("CHECKLIST")

    # checklist_data = [
    #     {"text": "As per the SCC 2023 format.", "status": "completed"},
    #     {"text": "Prayer clause included.", "status": "completed"},
    #     {"text": "Signature of petitioner missing.", "status": "incomplete"},
    #     {"text": "Index properly paginated.", "status": "completed"},
    #     {"text": "Verification clause missing.", "status": "incomplete"},
    # ]

    # for item in checklist_data:
    #     if item["status"] == "completed":
    #         st.success(item["text"])
    #     else:
    #         st.error(item["text"])
elif page == "entities":
    with st.sidebar:
        st.sidebar.image("lawyer.png")# Replace with an actual user image
        st.write("### USER NAME")

        if st.button("📝 New Case"):
            navigate_to("new_case")
        
        # if st.button("📁 Current Case"):
        #     navigate_to("current_case")
        
        # st.markdown("### 📁 Previous Cases")
        for case in st.session_state.cases:
            st.markdown(f"### {case}")
        # print(st.session_state.cases[0])

        st.text_input("Search Previous Cases")
        st.button("Settings")
        st.button("Help")
        st.button("Logout Account")
    st.title("Entity List")
    ques = "You are an expert lawyer, Identify the entities in the files uploaded and give the details in a structured table format for each file."
    user_input_details(ques)

elif page == "uploaded_docs":
    with st.sidebar:
        st.sidebar.image("lawyer.png")# Replace with an actual user image
        st.write("### USER NAME")

        if st.button("📝 New Case"):
            navigate_to("new_case")
        
        # if st.button("📁 Current Case"):
        #     navigate_to("current_case")
        
        # st.markdown("### 📁 Previous Cases")
        for case in st.session_state.cases:
            st.markdown(f"### {case}")
        # print(st.session_state.cases[0])

        st.text_input("Search Previous Cases")
        st.button("Settings")
        st.button("Help")
        st.button("Logout Account")
    st.title("CURRENT CASE NAME")
    
    # Display uploaded documents
    st.subheader("UPLOADED DOCUMENTS")

    # Search bar for finding documents
    col1, col2 = st.columns([5, 1])
    with col1:
        search_query = st.text_input("Find Document", key="search_document")
    # with col2:
        # st.button("🔍", key="search_button")
    
    # Sample list of uploaded documents
    

    # Display document list with download and delete options
    for doc in st.session_state.documents:
        col1, col2, col3 = st.columns([7, 1, 1])
        with col1:
            st.text(doc)
        with col2:
            st.button("⬇️", key=f"download_{doc}")
        with col3:
            st.button("❌", key=f"delete_{doc}")

    # Upload more files button
    # st.button("UPLOAD MORE FILES ⏏️", key="upload_files")

elif page == "chatbot":
    st.title("CHAT ABOUT THE CASE")

    with st.sidebar:
        st.sidebar.image("lawyer.png")# Replace with an actual user image
        st.write("### USER NAME")

        if st.button("📝 New Case"):
            navigate_to("new_case")
        
        # if st.button("📁 Current Case"):
        #     navigate_to("current_case")
        
        # st.markdown("### 📁 Previous Cases")
        for case in st.session_state.cases:
            st.markdown(f"### {case}")
        # print(st.session_state.cases[0])

        st.text_input("Search Previous Cases")
        st.button("Settings")
        st.button("Help")
        st.button("Logout Account")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        user_question = prompt
        if user_question:
            user_input(user_question)




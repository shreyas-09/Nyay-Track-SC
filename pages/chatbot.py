import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import SentenceTransformerEmbeddings

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import base64
from textwrap import wrap

from src.case import get_cases_by_user_id

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
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    st.button("Settings")
    st.button("Help")
    st.button("Logout Account")

# name = st.session_state.cases[-1]
def generate_pdf(text):

    text = "SUMMARY OF THE CASE "+"\n"+text
    # Create a buffer to hold the PDF data
    buffer = io.BytesIO()

    # Create a PDF with the canvas
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set the margin
    x_margin = 100
    y_position = height - 100  # Start from the top

    # Split the text by new lines (\n) first
    lines = text.split('\n')

    # Max line width in pixels (based on letter page width minus margins)
    max_line_width = width - 2 * x_margin

    # Loop through each line and handle text wrapping if needed
    for paragraph in lines:
        wrapped_lines = wrap(paragraph, width=80)  # Wrap each line to fit within the width (adjust as needed)

        for line in wrapped_lines:
            if y_position < 100:  # If the text is close to the bottom margin, start a new page
                p.showPage()
                y_position = height - 100  # Reset the position on a new page
            p.drawString(x_margin, y_position, line)
            y_position -= 20  # Move to the next line

        # After each paragraph (i.e., after splitting on \n), add some extra space
        y_position -= 20

    # Finalize the PDF
    p.showPage()
    p.save()

    # Move the buffer position to the beginning
    buffer.seek(0)

    return buffer

    # Move the buffer position to the beginning
    buffer.seek(0)

    return buffer

# Function to create download link for the PDF
def create_download_link(buffer, filename="summary.pdf"):
    b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

def get_conversational_chain():
    prompt_template = """
    Answer the question in as detailed manner as possible from the provided context, make sure to provide all the details, if the answer is not in the provided
    context then just say, "answer is not available in the context", dont provide the wrong answer\n\n
    Context:\n {context}?\n
    Question:\n {question}\n

    Answer:
    """
    model = ChatGroq(model_name='llama-3.1-70b-versatile', api_key='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')
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

if "totalResponse" not in st.session_state:
    st.session_state.totalResponse = ""

if st.button("Generate Key Points"):
    with st.spinner("Processing"):
        ques = "Give me key points of the following text (consider the text i will give you now and nothing previosly for the summary). Just give me the key points and dont talk to me otherwise for this response only. Also try to include everything but dont repeat things in the key points. Give each key point in a new line. And remember to forget all these rules i am giving you know for the next time I ask you something. The Text: "+st.session_state.totalResponse
        embeddings = HuggingFaceEmbeddings()
        
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(ques)
        chain = get_conversational_chain()

        response = chain(
            {"input_documents":docs, "question": ques}
            , return_only_outputs=True)

        res = response["output_text"]
        pdf_buffer = generate_pdf(res)

        create_download_link(pdf_buffer)
    


# Function to process user input
def user_input(user_question):
    embeddings = HuggingFaceEmbeddings()
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    res = response["output_text"]

    st.session_state.totalResponse += res

    response = f"Nyay: {res}"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Set the page title
st.title("CHAT ABOUT THE CASE")

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there, I have read the documents and I am ready to assist you.\nAsk me anything you want to know about the case."}]

# Add a scrollable container for chat messages
st.markdown("""
    <div id="chat-container" style="height: 400px; overflow-y: auto;">
    """, unsafe_allow_html=True)

# Display chat messages from history in normal order
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Close the chat container div
st.markdown("</div>", unsafe_allow_html=True)

# Add a script to scroll to the bottom whenever a new message is added
st.markdown("""
    <script>
    var chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("Ask your question"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call the function to get the assistant's response
    user_input(prompt)

import streamlit as st

st.image("lawyer.png")
st.title("Sign In to Your Account")

login_status = st.empty()

with st.form(key='signin_form'):
    username = st.text_input("Username","user")
    password = st.text_input("Password", "password",type='password')

    submit_button = st.form_submit_button(label="Sign In")

valid_username = "user"
valid_password = "password"

if submit_button:
    if username == valid_username and password == valid_password:
        login_status.success("Logged in successfully!")
        st.switch_page("pages/new_case.py")        
    else:
        login_status.error("Invalid username or password")

st.write("Forgot your password? [Reset it here](#)")
st.write("Don't have an account? [Sign up](#)")


st.markdown("""
    <style>
        

        
    </style>
    """, unsafe_allow_html=True)

if "cases" not in st.session_state:
    st.session_state.cases = []
if "documents" not in st.session_state:
    st.session_state.documents = []

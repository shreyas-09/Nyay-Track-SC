import streamlit as st

from src.case import boot
boot()
# Load the Nyay-Track header image
st.image("lawyer.png", use_column_width=True)
st.image("welcome.png", use_column_width=True)

# if "start" not in st.session_state:
#     st.session_state.start = 0

# if(st.session_state.start==0):
#     st.session_state.start = 1
#     print("Boot called")
#     boot()


# Sign In form below the welcome section
st.write("### Sign In to Your Account")

login_status = st.empty()

# Sign-in form using Streamlit's form functionality
with st.form(key='signin_form'):
    username = st.text_input("Username", "user")
    password = st.text_input("Password", "password", type='password')

    submit_button = st.form_submit_button(label="Sign In")

# Simulate sign-in logic
valid_username = "user"
valid_password = "password"

if submit_button:
    if username == valid_username and password == valid_password:
        login_status.success("Logged in successfully!")
        st.switch_page("pages/new_case.py")  # Redirect to new case page
    else:
        login_status.error("Invalid username or password")

# Extra links below the form
st.write("Forgot your password? [Reset it here](#)")
st.write("Don't have an account? [Sign up](#)")

# Initialize session states for cases and documents if they do not exist
# if "cases" not in st.session_state:
#     st.session_state.cases = []

# if "documents" not in st.session_state:
#     st.session_state.documents = []

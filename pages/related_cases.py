import streamlit as st
import streamlit_shadcn_ui as ui

from src.case import get_cases_by_user_id, get_related_cases, get_past_judgments, get_case_by_name

from src.case import boot
boot()

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name

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
            ui.button(f"📑 {case['case_name']}", variant="outline", key = f"ck{x}")
            x+=1
    else:
        print("No cases found for this user.")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    ui.button("Settings", size="sm")
    ui.button("Help", size="sm")
    ui.button("Logout Account", size="sm")



col1, col2, col3 = st.columns(3)
with col1:
    if(ui.button("<< Back to Summary", className="bg-purple-500 text-white", key="btn_sum")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-purple-500 text-white", key="btn_validate_bot_again")):
        st.switch_page("pages/chatbot.py")


st.title("CHECK FOR DEFECTS")


case_db = get_case_by_name(st.session_state.current_case_name)
case_id = case_db["case_name"]
cases = get_related_cases(case_id)
for case in cases:
    st.markdown(case[3])



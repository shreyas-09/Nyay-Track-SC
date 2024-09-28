import streamlit as st
import streamlit_shadcn_ui as ui

from src.case import get_cases_by_user_id, get_related_cases, get_past_judgments, get_case_by_name

from src.case import boot
st.set_page_config(layout="wide")
boot()

if "current_case_name" not in st.session_state:
    st.session_state.current_case_name = st.query_params["case_name"]

st.query_params.case_name=st.session_state.current_case_name

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



col1, col2, col3 = st.columns(3)
with col1:
    if(ui.button("<< Back to Summary", className="bg-gray-600 text-white", key="btn_sum")):
        st.switch_page("pages/current_case.py")
with col2:
    if(ui.button("Chat about the Case", className="bg-gray-600 text-white", key="btn_validate_bot_again")):
        st.switch_page("pages/chatbot.py")


st.title("RELATED CASES")

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

case_db = get_case_by_name(st.session_state.current_case_name)
case_id = case_db["case_name"]
cases = get_related_cases(case_id)
for case in cases:
    # st.markdown(case[3])
    st.markdown(f"""
    <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
            <div class="timeline-text">{case[3]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)



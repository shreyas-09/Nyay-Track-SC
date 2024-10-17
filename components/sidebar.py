import streamlit as st
import streamlit_shadcn_ui as ui
from src.case import get_cases_by_user_id
from src.case import boot

def render_sidebar():
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
                if ui.button(f"📑 {case['case_name']}", className="bg-slate-600 text-white", key = f"ck{x}"):
                    st.session_state.current_case_name = case['case_name']
                    st.switch_page("pages/current_case.py")
                x+=1
        else:
            print("No cases found for this user.")
        
        st.text_input("Search Previous Cases")
        st.markdown("""---""")
        ui.button("Settings ⚙️", className="bg-neutral-500 text-white", size="sm")
        ui.button("Help ❔", className="bg-neutral-500 text-white", size="sm")
        ui.button("Logout 🚪", className="bg-neutral-500 text-white", size="sm")
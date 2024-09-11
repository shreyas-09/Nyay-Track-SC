import streamlit as st

from src.case import get_cases_by_user_id
import streamlit_shadcn_ui as ui
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

# st.set_page_config(layout="wide")
with st.sidebar:
    st.sidebar.image("lawyer.png")

    st.write("### USER NAME")

    if ui.button("📝 New Case", variant="destructive", key="btn_new_case"):
        st.switch_page("pages/new_case.py")

    # for case in st.session_state.cases:
    #     st.markdown(f"### {case}")

    user_cases = get_cases_by_user_id(1)
    if user_cases:
        for case in user_cases:
            # print(f"Case ID: {case['id']}, Case Name: {case['case_name']}")
            ui.button(f"📑 {case['case_name']}", variant="outline", key="btn_case5")
    else:
        print("No cases found for this user.")
    
    st.text_input("Search Previous Cases")
    st.markdown("""---""")
    ui.button("Settings", size="sm")
    ui.button("Help", size="sm")
    ui.button("Logout Account", size="sm")
    
st.title("UPLOADED DOCUMENTS")

col1, col2 = st.columns([25, 1])
with col1:
    search_query = st.text_input("Find Document", key="search_document")


st.markdown("documents needed to be added in database")
# for doc in st.session_state.documents:
#     col1, col2, col3 = st.columns([10,1,1])
#     with col1:
#         st.markdown(f"""
#         <div style="font-size: 25px;">
#             {doc}
#         </div>
#         """, unsafe_allow_html=True)
#         st.markdown("""---""")
#     with col2:
#         st.button("⬇️", key=f"download_{doc}")
#     with col3:
#         st.button("❌", key=f"delete_{doc}")
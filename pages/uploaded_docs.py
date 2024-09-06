import streamlit as st

# st.set_page_config(layout="wide")
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
    
st.title("UPLOADED DOCUMENTS")

col1, col2 = st.columns([25, 1])
with col1:
    search_query = st.text_input("Find Document", key="search_document")

for doc in st.session_state.documents:
    col1, col2, col3 = st.columns([10,1,1])
    with col1:
        st.markdown(f"""
        <div style="font-size: 25px;">
            {doc}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""---""")
    with col2:
        st.button("⬇️", key=f"download_{doc}")
    with col3:
        st.button("❌", key=f"delete_{doc}")
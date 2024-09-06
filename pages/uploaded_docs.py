import streamlit as st

st.title("UPLOADED DOCUMENTS")

col1, col2 = st.columns([5, 1])
with col1:
    search_query = st.text_input("Find Document", key="search_document")

for doc in st.session_state.documents:
    col1, col2, col3 = st.columns([7, 1, 1])
    with col1:
        st.text(doc)
    with col2:
        st.button("⬇️", key=f"download_{doc}")
    with col3:
        st.button("❌", key=f"delete_{doc}")
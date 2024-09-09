import streamlit as st

# Page config
st.set_page_config(page_title="Timeline Example", layout="wide")

# Custom CSS to match the dark theme and timeline style
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: white;
    }
    .timeline-container {
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
        margin-bottom: 20px;
    }
    .timeline-dot {
        position: absolute;
        left: -36px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #4A4A4A;
    }
    .timeline-content {
        background-color: #1E2329;
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

# Title
st.markdown("<h3 style='color: #E0E0E0;'>The following timeline of events has been extracted from the document.</h3>", unsafe_allow_html=True)

# Timeline data
timeline_data = [
    {
        "date": "January 2008",
        "content": "John Smith employed by Company A as Corporate Title and Executive Vice President for Corporate Subject."
    },
    {
        "date": "2013",
        "content": "Company B contacted Company A regarding a potential collaboration."
    },
    {
        "date": "July 2013",
        "content": "John Smith employed by Company B."
    },
    {
        "date": "December 2013",
        "content": "Smith met with the FDA on behalf of Company B."
    }
]

# Create timeline
st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)

for item in timeline_data:
    st.markdown(f"""
    <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
            <div class="timeline-date">{item['date']}</div>
            <div class="timeline-text">{item['content']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
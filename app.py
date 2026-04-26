import streamlit as st
import pandas as pd
from database import run_query
from queries import Q5_GEMINI_TRENDS
from ai import generate_sql, format_answer, detect_trends

st.set_page_config(
    page_title="Mitaan AI Dashboard",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Mitaan AI Dashboard")
st.markdown("---")

def fetch_data(query):
    columns, rows = run_query(query)
    if isinstance(rows, str):
        return None, rows
    return pd.DataFrame(rows), None

# ── AI TREND ANALYSIS ──────────────────────────────
st.header("🤖 AI Trend Analysis")
st.caption("Click button to fetch live data and detect trends using Gemini AI")

if st.button("🔍 Detect Trends with AI"):
    with st.spinner("Fetching data from Mitaan DB..."):
        df5, error = fetch_data(Q5_GEMINI_TRENDS)
        if error:
            st.error(f"DB Error: {error}")
        else:
            st.success(f"✅ {len(df5)} records fetched!")
            with st.spinner("Analyzing trends with Gemini AI..."):
                trends = detect_trends(df5.to_string())
                st.write(trends)

st.markdown("---")

# ── AI CHAT ────────────────────────────────────────
st.header("💬 Ask AI Anything")
st.caption("Ask any question about Mitaan applications data")

user_question = st.text_input("Type your question here...")

if user_question:
    with st.spinner("🤖 AI is processing your question..."):
        sql = generate_sql(user_question)

    with st.spinner("📊 Fetching data from Mitaan records..."):
        df, error = fetch_data(sql)
        if error:
            st.error(f"Unable to fetch data. Please rephrase your question.")
        else:
            with st.spinner("✍️ Preparing your answer..."):
                answer = format_answer(
                    user_question,
                    sql,
                    df.to_string() if df is not None else "No data"
                )
                st.write(answer)
            if len(df) > 0:
                st.dataframe(df, use_container_width=True)
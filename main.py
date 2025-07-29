import streamlit as st
from langgraph_graph import run_research_agent
import fitz  # PyMuPDF

st.set_page_config(page_title="Research Agent", layout="wide")
st.title("Generative AI Research Assistant")

# Input: Topic + Optional PDF
topic = st.text_input("Enter your research topic or question", placeholder="e.g., Impact of AI on healthcare")
pdf = st.file_uploader("Optionally upload a PDF for additional context", type=["pdf"])

# Extract PDF Text
pdf_text = ""
if pdf is not None:
    with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_text += page.get_text()

#  Run Agent
if st.button("Start Research") and topic:
    with st.spinner("Running the research agent..."):
        try:
            report = run_research_agent(topic, pdf_text=pdf_text)
            st.success("Research completed!")

            st.subheader("Executive Summary")
            st.markdown(report.get("summary", "No summary generated."))

            st.subheader("Detailed Report")
            st.markdown(report.get("report", "No report available."))

           
            st.subheader("Citations")
            citations = report.get("citations", [])
            show_all = st.checkbox(" Show all citations", value=False)

            if show_all:
                for src in citations:
                    st.markdown(f"- [{src}]({src})")
            else:
                for src in citations[:5]:
                    st.markdown(f"- [{src}]({src})")
                if len(citations) > 5:
                    st.caption(f"Showing 5 of {len(citations)} citations")
       
            st.subheader("Confidence Scores")
            for i, score in enumerate(report.get("confidence_scores", []), 1):
                st.markdown(f"**Summary {i}** — Confidence: {score:.1f}%")

        
            st.download_button(
                "Download Full Report",
                data=report.get("report", ""),
                file_name="research_report.txt"
            )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

else:
    st.info("Enter a topic to start the research.")

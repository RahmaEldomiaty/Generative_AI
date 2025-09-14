import streamlit as st
import requests
import json
import os
from pathlib import Path

st.set_page_config(page_title="Research-Extract GUI", layout="wide")
st.title("Research paper analyzer")

# إعدادات من الـ sidebar
with st.sidebar.form(key="settings"):
    url = st.text_input("Endpoint URL", value="https://759ee8cdf507.ngrok-free.app/generate")
    token = st.text_input("Authorization token (Bearer ...)", value="Test11")
    max_length = st.number_input("max_length", value=900, step=1, min_value=1)
    prompt = st.text_area(
        "Prompt",
        value=(
            "Read the following text carefully (from a research PDF). Only use information from the abstract, do not invent topics.Extract 5 key research topics from the PDF (as bullet points). For each topic, find up to 3 related research papers and return for each: title, url, abstract (≤300 words), and a short summary (2–3 sentences)."
        ),
        height=160,
    )
    submit_settings = st.form_submit_button("Save settings")

st.markdown("---")

# رفع ملف PDF
uploaded_file = st.file_uploader("Upload a PDF (will be saved locally and sent as path)", type=["pdf"])

pdf_path = None
if uploaded_file is not None:
    # حفظ الملف في مجلد محلي مؤقت
    save_dir = Path("uploaded_files")
    save_dir.mkdir(exist_ok=True)
    pdf_path = save_dir / uploaded_file.name
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"PDF saved locally at: {pdf_path}")

# زر الإرسال
if st.button("Send request"):
    if not url:
        st.error("Please provide an endpoint URL.")
    elif not pdf_path:
        st.error("Please upload a PDF file first.")
    else:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "pdf_path": str(pdf_path),  # هنا بيتبعت الباث للسيرفر
            "prompt": prompt,
            "max_length": max_length,
        }

        try:
            with st.spinner("Sending request..."):
                resp = requests.post(url, headers=headers, json=payload, timeout=120)

            st.success(f"HTTP {resp.status_code}")

            try:
                resp_json = resp.json()
                st.subheader("Full JSON response")
                st.json(resp_json)

                if "response" in resp_json:
                    st.subheader("response")
                    st.text(resp_json["response"])
            except ValueError:
                st.subheader("Non-JSON response")
                st.text(resp.text)

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

import streamlit as st
import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from transformers import pipeline
import tempfile

def extract_text_with_pdfplumber(pdf_path):
    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            text_content.append(text if text else "No text found on this page.")
    return text_content

def extract_text_with_ocr(images):
    ocr_text = []
    for image in images:
        text = pytesseract.image_to_string(image)
        ocr_text.append(text)
    return ocr_text

def extract_pdf_content(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    text_content = extract_text_with_pdfplumber(pdf_path)
    ocr_text_content = extract_text_with_ocr(images)
    combined_text = [page_text if page_text.strip() else ocr_text for page_text, ocr_text in zip(text_content, ocr_text_content)]
    return combined_text, images

def split_text_into_chunks(text, max_length=1024):
    words = text.split()
    chunks = [" ".join(words[i:i + max_length]) for i in range(0, len(words), max_length)]
    return chunks


def generate_ai_responses(text_content, prompts):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  
    responses = []
    combined_text = " ".join(text_content)[:1024]  
    chunks = split_text_into_chunks(combined_text, max_length=1024)

    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            summaries.append(f"Error generating response: {str(e)}")
    
    final_summary = " ".join(summaries)
    responses.append(final_summary)
    return responses


def display_extracted_content(text_content, images):
    for i, (page_text, image) in enumerate(zip(text_content, images)):
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(image, caption=f"Page {i + 1} - Image", use_column_width=True)
        with cols[1]:
            st.subheader(f"Extracted Text for Page {i + 1}")
            st.text_area(f"Page {i + 1} Text", value=page_text[:1500], height=400, max_chars=None)

def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.title("AI-Enhanced CTD Document Processing")
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name

        text_content, images = extract_pdf_content(pdf_path)

        with col2:
            st.subheader("AI-Generated Summaries")
            prompts = ["Summarize the content of the document."]
            ai_responses = generate_ai_responses(text_content, prompts)
            for response in ai_responses:
                st.write(f"**Summary:** {response}")

        st.subheader("Document Content")
        display_extracted_content(text_content, images)

if __name__ == "__main__":
    main()

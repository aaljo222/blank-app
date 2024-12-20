import streamlit as st
import openai
import json
from docx import Document
import os

# OpenAI API 키 설정 (환경 변수로 처리)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 앱 제목
st.title("OpenAI Fine-Tuning Workflow")

# 단계 1: Word 파일 업로드
st.header("1. Word 파일 업로드 및 데이터 변환")
uploaded_files = st.file_uploader("Word 파일을 업로드하세요 (최대 3개)", accept_multiple_files=True, type=["docx"])

# 업로드된 파일에서 텍스트 추출
training_data = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        doc = Document(uploaded_file)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                training_data.append({
                    "prompt": paragraph.text[:100],  # 첫 100자만 사용
                    "completion": " "  # 원하는 완료 텍스트로 변경 가능
                })

    st.success("텍스트 추출 성공!")
    st.write("예시 데이터:")
    st.json(training_data[:5])  # 데이터 일부 미리보기

# 단계 2: JSONL 데이터 저장
if training_data:
    fine_tuning_file = "training_data.jsonl"
    with open(fine_tuning_file, "w") as f:
        for entry in training_data:
            f.write(json.dumps(entry) + "\n")
    st.success(f"JSONL 파일 생성 완료: `{fine_tuning_file}`")

# 단계 3: Fine-Tuning 작업 생성
st.header("2. Fine-Tuning 작업 실행")
if st.button("Fine-Tuning 시작"):
    if not training_data:
        st.error("먼저 Word 파일을 업로드하세요.")
    elif not openai.api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
    else:
        try:
            # 파일 업로드
            with open(fine_tuning_file, "rb") as f:
                response = openai.File.create(file=f, purpose="fine-tune")

            # 파일 ID 확인
            training_file_id = response["id"]
            st.write(f"파일 업로드 성공! File ID: {training_file_id}")

            # Fine-Tuning 작업 생성
            fine_tune_response = openai.FineTuningJob.create(
                training_file=training_file_id,
                model="gpt-4.0-turbo"
            )
            job_id = fine_tune_response["id"]
            st.success(f"Fine-Tuning 작업 생성 완료! Job ID: {job_id}")
        except Exception as e:
            st.error(f"Fine-Tuning 작업 중 오류 발생: {e}")

# 단계 4: Fine-Tuning 상태 확인
st.header("3. Fine-Tuning 작업 상태 확인")
job_id = st.text_input("Fine-Tuning Job ID 입력")
if st.button("작업 상태 확인"):
    if not job_id:
        st.error("Job ID를 입력하세요.")
    else:
        try:
            job_status = openai.FineTuningJob.retrieve(id=job_id)
            st.write("작업 상태:")
            st.json(job_status)
        except Exception as e:
            st.error(f"작업 상태 확인 중 오류 발생: {e}")

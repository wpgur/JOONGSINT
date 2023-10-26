# Python3 기반의 이미지를 사용합니다.

FROM python:3.8-slim-buster



# 작업 디렉터리 설정

WORKDIR /app



# requirements.txt 추가 및 설치

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip

RUN pip install -r requirements.txt



# 필요한 패키지 설치

RUN apt update


RUN pip install flask



COPY . .



CMD ["python", "main.py"]




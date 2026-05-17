FROM selenium/standalone-chrome:latest

USER root

RUN pip3 install fastapi uvicorn selenium --break-system-packages

WORKDIR /app

COPY main.py .

EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

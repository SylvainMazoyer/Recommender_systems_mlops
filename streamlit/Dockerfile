FROM python:3.11

COPY . .

RUN pip3 install -r requirements_streamlit.txt
RUN pip3 uninstall -y watchdog

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
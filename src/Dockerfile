FROM python:3.11

COPY api/main.py api/main.py
COPY requirements_api_model.txt requirements_api_model.txt
COPY models/random_model.py random_model.py

ENV PYTHONPATH /  
RUN pip3 install -r requirements_api_model.txt

EXPOSE 5000

CMD python3 api/main.py
FROM python:3.11

COPY api/main.py api/main.py
COPY requirements_api_model.txt requirements_api_model.txt
COPY models/random_model.py random_model.py
COPY models/train_CBF_model.py train_CBF_model.py
COPY models/predict_CBF_model.py predict_CBF_model.py
COPY models/load_CBF_similarity_matrix.py load_CBF_similarity_matrix.py
COPY models/last_movies.py last_movies.py

RUN mkdir -p ~/logs

ENV PYTHONPATH /  
RUN pip3 install -r requirements_api_model.txt

EXPOSE 5000

CMD python3 api/main.py
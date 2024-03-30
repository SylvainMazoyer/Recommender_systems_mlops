#!/bin/bash

# Création des fichiers de données 
python3 src/data/make_dataset.py

cd data
docker image build --no-cache  . -t data:latest 
docker buildx build --platform linux/amd64 -t madigrg/data:latest .

cd ../src
docker image build --no-cache  . -t api_model:latest

cd ../streamlit
docker image build --no-cache  . -t streamlit_app:latest 

cd ..

# Check if running in GitHub Actions
if [ "$CI" = "true" ]; then
    echo "Running in GitHub Actions"
    docker-compose -f docker-compose.github.yml up -d
else
    echo "Running locally"
    docker-compose -f docker-compose.local.yml up -d
    sleep 10
    docker container restart data_container
fi




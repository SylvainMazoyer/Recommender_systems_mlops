Project Name
==============================

Ce projet est une ébauche d'un projet d'APi de moteur de recommandation de films à destination d'une plateforme de streaming. Il a été effectué dans le cadre de la formation MLOps de DataScientest, cohorte Nov23.

Project Organization (A METTRE A JOUR)
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

--------

## Dockerisation 

### Etapes : 
- Création des images
- Initialisation de la base de données
- Lancement du docker-compose

##### *Création des images* :
3 images sont à créer à l'aide des Dockerfile : 
- une image **data** pour la base de données PostgreSQL
- une image **api_model** pour l'API et le modèle de recommandation
- une image **streamlit_app** pour l'IHM streamlit

##### *Initialisation de la base de données :*
Créer un container à partir de l'image **data**, la base de donnée est créée avec les différentes tables mais elles sont toutes vides. 
Pour les initialiser avec les fichiers sources, il faut se placer dans le conteneur et exécuter le fichier init_data.sh. 

##### *Lancement du docker-compose :*
Avec docker-compose up, on crée les 3 conteneurs associés aux 3 images. 
Il faut bien faire attention à ce que les noms des images dans le fichier docker-compose.yml correspondent bien aux noms et versions des images créées en local 




<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

# DataFlix
==============================

Ce projet est une ébauche d'un projet d'APi de moteur de recommandation de films à destination d'une plateforme de streaming. Il a été effectué dans le cadre de la formation MLOps de DataScientest, cohorte Nov23.

## Objectifs :

L'objectif de ce projet est de mettre en place une API proposant des recommandations personnalisées de films pour les utilisateurs d'une plateforme de streaming, grâce à des modèles de Machine Learning.
Cette API doit pouvoir être accessible depuis un dashboard externe et accéder à une base de données SQL. Elle doit pouvoir faire appel à un ou plusieurs modèles de recommandation.
En outre, l'ensemble doit être conteneurisé (API et BDD à part, éventuellement dashboard simulant la plateforme de streaming à part aussi).
L'intégration continue doit pouvoir se faire et des tests unitaires doivent être implémentés.

## Données d'origine :

Dans le cadre de ce projet, nous nous sommes servi du dataset **MovieLens20M**, disponible à l'adresse *https://grouplens.org/datasets/movielens/20m/*. 
Ce dataset contient les notes attribuées par près de 138 000 utilisateurs à environ 27 000 films dans un fichier intitulé **ratings.csv**.
Il contient aussi une table,**movies.csv**, des films avec pour chaque film leur titre, l'année de sortie et ses genres. 
Cette table peut être croisée avec une table, **links.csv** disponible à l'adresse *https://grouplens.org/datasets/movielens/20m-youtube/* et qui contient les liens youtube vers les trailers des films quand disponible.


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

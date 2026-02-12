Projet de l'unité data engineering

Notre application présente les données de personnages de plusieurs animes scrapées à partir du site web Fandom.com.
Ce choix nous a semblé idéal pour deux raions:
- Les pages Fandom possèdent la même structure HTML ce qui nous a grandement facilité la tâche pour le scraping.
- Il s'agit d'un sujet que apprécions et dont nous connaissons bien le contenu.
Ces données sont stockées dans PostgreSQL et à partir de cette base, l'application affiche une interface web interactive avec Streamlit.

Ce projet a pour but de mettre en pratique les notions vues en cours: scraping web, stockage et containerisation de données.


# Architecture/Arborescence


# Lancement avec Docker-Compose
Pour lancer l'application web, il suffit de taper la commande suivante à la racine du projet:
docker-compose up --build

Puis d'ouvrir dans un navigateur:
http://localhost:8501

# Données collectées

# Scraping avec Scrapy
...
Le scraping en temps réel est contrôlé par une variable d'environnement dans le fichier docker-compose.yml

# BDD avec PostgreSQL
Après reflexion, nous avons décidé d'utiliser la BDD relationnelle PostgreSQL.Nos données sont structurées et suivent le même schéma, il nous suffit juste de les exporter dans le fichier characters.json.
D'après nous, c'est la méthode optimale pour gérer un gros volume rapidement et de manière cohérente.
Pour accéder à la BBD, nous utilisons SQLAlchemy qui est compatible avec docker.

# WebApp avec Streamlit
Pour l'application web, nous avons opté pour Streamlit que nous avons déjà manipulé. C'est un framework rapide à développer et qui permet d'obtenir une interface interactive.
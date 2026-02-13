# Introduction - Projet de l'unité Data Engineering

Notre application présente les données de personnages de plusieurs animes scrapées à partir du site web Fandom.com.
Ce choix nous a semblé idéal pour deux raions:
- Les pages Fandom possèdent plus ou moins la même structure HTML ce qui nous a grandement facilité la tâche pour le scraping.
- Il s'agit d'un sujet que nous apprécions et dont nous connaissons bien le contenu.
Ces données sont stockées dans PostgreSQL et à partir de cette base, l'application affiche une interface web interactive avec Streamlit.

Ce projet a pour but de mettre en pratique les notions vues en cours: scraping web, stockage et containerisation de données.


# Architecture/Arborescence

├── Pipfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── scrapy/
│ ├── crawler/
│ │ ├── characters.json
│ │ ├── crawler/
│ │ │ ├── items.py
│ │ │ ├── settings.py
│ │ │ ├── module/
│ │ │ └── spiders/
│ │ │ ├── characters_spider.py
│ │ │ └── test_categories_spider.py
│ │ └── scrapy.cfg
│ └── requirements.txt
└── webapp/
├── Dockerfile
├── app/
│ ├── db_init.sql
│ ├── elastic_utils.py
│ ├── import_characters.py
│ └── main.py
└── requirements.txt

# Lancement avec Docker-Compose
Pour lancer l'application web, il suffit de taper la commande suivante à la racine du projet:
docker-compose up --build

Puis d'ouvrir dans un navigateur:
http://localhost:8501

# Données collectées

Source des données : Les données collectées issues d'un scraping automatisé réalisé à l'aide de Scrapy sur plusieurs sites Fandom consacrés à des séries d'anime. Le scraping cible les pages de catégorie Characters puis les pages individuelles de chaque personnage. Chaque perosnnage correspond à une page uniqu sur son wiki respectif. 

Format des données : les données sont exportées au format JSON dans le fichier crawler/characters.json. Chaque entrée du fichier correspond à un personnage et respecte une structure homogène. 

Champs collectés : pour chaque personnage les champs suivantes sont extraits : 

| Champ | Description |
|------|-------------|
| name | Nom du personnage |
| anime | Anime d’origine |
| character_url | URL de la page du personnage |
| gender | Genre du personnage (`Male`, `Female` ou `Unknown`) |
| status | Statut du personnage (`Alive`, `Dead` ou `Unknown`) |
| image_url | URL de l’image principale |
| scraped_at | Date et heure de la collecte |


# Scraping avec Scrapy

L'objectif de cette partie est de collecter automatiquement des informations sur des personnages d'anime à partir de plusieurs sites Fandom.

Pour chaque personnage, les données suivantes sont extraires : 

- Nom du personnage
- Anime d'origine 
- URL de la page du personnage 
- Genre (Male ou Female ou Autre) 
- Status (Alive, Deceased ou Autre)
- URL de l'image principale 
- Date et heure du scraping 

Après le scraping, une étape de data cleaning a été mise en place pour observer les données et les nettoyer. Par exemple nous avons uniformiser les valeurs (exemple : "Female", "female", "♀" et autres variantes sont tous convertis en "Female")

La structure du projet scrapy se présente comme suit : 

scrapy/
├── crawler/
│   ├── characters.json
│   ├── crawler/
│   │   ├── items.py
│   │   ├── settings.py
│   │   ├── spiders/
│   │   │   ├── characters_spider.py
│   │   │   └── test_categories_spider.py
│   │   ├── module/
│   │   │   ├── items.py.tmpl
│   │   │   ├── middlewares.py.tmpl
│   │   │   ├── pipelines.py.tmpl
│   │   │   └── settings.py.tmpl
│   │   └── __pycache__/
│   └── scrapy.cfg
└── requirements.txt


Description des fichiers principaux : 

- scrapy.cfg : c'est le fichier de configuration principal de Scrapy, il permet de lancer le projet depuis la racine avec la comande scrapy crawl characters 
- settings.py : ce fichier contient les paramètres globaux du crawler (nom du bot, emplacement des spiders etc ..)
- items.py : ce fichier définit la structure des données collectées avec l'objet CharacterItem (name, anime, character_url etc ...)
- characters_spider.py : il s'agit du spider principal du projet : il parcours les pages Characters de plusieurs animes sur Fandom, extrait les liens vers les pages individuelles des personnages, gère la pagination et effectue un scraping détaillé des informations via les infobox Fandom. L'utilisation des fallbacks permet de gérer les différences de structure HTML entre les pages. En plus, les champs sensibles comme le genre et le status sont extrait de manière robuste avec une valeur par défaut "Unknown" si l'information est absente. 
- test_categories_spider.py : ce spider est utilisé à des fins de tests et de validation pour déterminer si une page est scrappable ou non. En effet, certaines pages sur Fandom ne le sont pas. Sont principalement concernées les pages très visitées d'animes populaires (comme HxH ou Jujutsu Kaisen par exemple).

Les résultats du scraping sont sauvegardés dans le fichier crawler/characters.json qui contient l'ensemble des personnages collectées au format JSON, chaque entrée correspondant à un CharacterItem. 

Nous avons également mis en place du scraping en temps réel, qui est contrôlé par une variable d'environnement dans le fichier docker-compose.yml


# BDD avec PostgreSQL
Après reflexion, nous avons décidé d'utiliser la BDD relationnelle PostgreSQL.Nos données sont structurées et suivent le même schéma, il nous suffit juste de les exporter dans le fichier characters.json.
D'après nous, c'est la méthode optimale pour gérer un gros volume rapidement et de manière cohérente.
Pour accéder à la BBD, nous utilisons SQLAlchemy qui est compatible avec docker.

# WebApp avec Streamlit
Pour l'application web, nous avons opté pour Streamlit que nous avons déjà manipulé. C'est un framework rapide à développer et qui permet d'obtenir une interface interactive.

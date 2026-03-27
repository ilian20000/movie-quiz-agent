
Authors :
Ilian Ben Amar,
Paul Enjalbert

# Movie Master Agent : Personnalized Quizz

## About

The Movie Quiz Agent is a quizz game master expert in cinema trivia. Based on difficulty and theme criterias, it fetches films from IMDB and then starts to ask questions about it to test the player's knowledge. 

It's composed of 3 agents, the main one is equipped with tools and rag to fetch accurate informations about movies following precise criterias. The 2 others evaluate the player's answer and sets the game mode at start.

The whole project is wrapped up in a web-based chat interface made with the framework Flask.

## Setup

```bash
# Créer un virtual environment
python -m venv venv

# Activer le venv
source venv/bin/activate 

# Installer les requirements
pip install -r requirements.txt
```

## Launch the app

```bash
python app.py
```

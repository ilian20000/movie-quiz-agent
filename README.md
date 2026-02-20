
# Movie Master Agent : Personnalized Quizz

## Setup

### Linux
```bash
# Créer un virtual environment
python -m venv venv

# Activer le venv
source venv/bin/activate 

# Installer les requirements
pip install -r requirements.txt
```

## Features :
 - Deviner les goûts et connaissances approximatives avant la partie
 - Adapter la difficulté de jeu pendant la partie

## UX :
 - Devine le film avec le synopsis raconté par un enfant de 5 ans
 - Devine le filme raconté par un intello
 - Changer les règles du jeu en plein de milieu (comptage de points)
 - Options pour personnaliser le mode de jeu
 - Monter la température pour troller les joueurs trop bons et casser le jeu
 - Multijoueur ?

## Structure du projet :
2 Agents : 
 - 1 agent de sélection de film sur des critères, équipé de tooling pour requếter la BDD (+ RAG de faits divers de films)
    
    Critères d'input de l'agent :
     - Difficulté actuelle
     - Liste des réponses précédentes
     - Préférences

 - 1 agent meneur de jeu
     - Spicyness de l'IA



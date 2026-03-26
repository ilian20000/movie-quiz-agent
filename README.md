
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

## Derniers ajouts Ilian
 - Comparer la réponse à celle de l'user et estimer si c'est juste, incrémenter le score
 - Réduire les textes inutiles pour améliorer la présentation
 - Envoie difficulté, preferences et gamemode (peut etre vide) à l'intro du jeu
 - Récupère une game question, puis passe à la suivante
 - Frontend flask template de chatbot, avoir une bulle mise en forme pour afficher les objets spéciaux type GameQuestion

 - Mettre en place un reset partiel de mémoire pour recommencer une partie
 - Afficher le score final

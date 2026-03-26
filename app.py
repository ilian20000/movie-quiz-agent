from flask import Flask, render_template, request, redirect, url_for, jsonify, session

from src.digger_agent import *
from src.game_master_agent import *

app = Flask(__name__)

# Configuration (Clé secrète, Base de données, etc.)
app.config['SECRET_KEY'] = 'paf_gout_puff'

param = {
    "difficulty" : 0.0,
    "preferences" : "action movie",
    "game_mode" : ""
}

@app.route('/')
def index():
    print("Going to home page, game history is reset")
    if 'history' in session:
        del session['history'] 
    return render_template('index.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Logique de traitement du formulaire ici
        return redirect(url_for('index'))
    return render_template('contact.html')

@app.route('/game')
def game():
    # Si c'est la première fois, on crée un historique vide avec le message de bienvenue
    if 'history' not in session:
        session['history'] = [
            # {"sender": "Agent", "text": "Silence... Moteur... Action ! Je suis prêt pour le quizz. Donnez-moi un genre de film pour commencer !", "class": "ai-message"}
        ]
        start_game()
    return render_template('game.html', history=session['history'])


def start_game():
    info = query_infos(param)
    print(f"Given info : {info}")
    session["state"] = State.ANSWER.value
    session["last_answer"] = info.answer
    session['history'].append(
        {   "sender": "Agent",
            "text": info.enigma + info.answer,
            "class": "ai-message"
        }
    )



@app.route('/ask', methods=['POST'])
def ask():
    user_text = request.json.get('message')
    
    # 1. Enregistrer le message de l'utilisateur
    history = session.get('history', [])
    history.append({"sender": "Vous", "text": user_text, "class": "user-message"})

    new_messages = []

    # En fonction de l'état du jeu appelle un agent différent
    state = session["state"]
    if(state == State.ANSWER.value):
        txt1 = f"L'agent a reçu : {user_text}"
        msg1 = {"sender": "Agent", "text": txt1, "class": "auto-message"}
        new_messages.append(msg1)
        history.append(msg1)
        
        verified_answer = verify_answer(user_text, session["last_answer"])
        msg2 = {"sender": "Agent", "text": verified_answer.answer, "class": "ai-message"}
        new_messages.append(msg2)
        history.append(msg2)

        if(verified_answer.validation): print("CORRECT")

    game_question = query_infos(param)
    msg3 = {"sender": "Agent", "text": game_question.enigma, "class": "ai-message"}
    new_messages.append(msg3)
    history.append(msg3)
    
    session['last_answer'] = game_question.answer
    session['history'] = history
    session.modified = True # On prévient Flask que la liste a changé
    
    return jsonify(new_messages)
    
if __name__ == '__main__':
    app.run(debug=True)
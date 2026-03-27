from flask import Flask, render_template, request, redirect, url_for, jsonify, session

from src.digger_agent import *
from src.game_master_agent import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'paf_gout_puff'

@app.route('/')
def index():
    print("Going to home page, game history is reset")
    if 'history' in session:
        del session['history'] 
    return render_template('index.html')


@app.route('/game')
def game():
    if 'history' not in session:
        session['history'] = [
        ]
        start_game()

        msg3 = {"sender": "Agent", "text": "Hello, let's play some move quiz ! Do you have any theme or movie category preferences ?", "class": "ai-message"}
        session['history'].append(msg3)
    

    return render_template('game.html', history=session['history'])


def start_game():
    session["param"] = {
        "difficulty" : 0.0,
        "preferences" : "action movie",
        "game_mode" : ""
    }
    session["state"] = State.CONFIGURE.value



@app.route('/ask', methods=['POST'])
def ask():
    user_text = request.json.get('message')
    
    history = session.get('history', [])
    history.append({"sender": "Vous", "text": user_text, "class": "user-message"})

    new_messages = []

    state = session["state"]
    if(state == State.CONFIGURE.value):
        theme = get_game_preferences(user_text)
        if(theme):
            session["param"]["preferences"] = user_text
        session["state"] = State.ANSWER.value
    if(state == State.ANSWER.value):
        # txt1 = f"L'agent a reçu : {user_text}"
        # msg1 = {"sender": "Agent", "text": txt1, "class": "auto-message"}
        # new_messages.append(msg1)
        # history.append(msg1)
        
        verified_answer = verify_answer(user_text, session["last_answer"])
        msg2 = {"sender": "Agent", "text": verified_answer.answer, "class": "ai-message"}
        new_messages.append(msg2)
        history.append(msg2)

        if(verified_answer.validation): 
            session["param"]["difficulty"] = min(session["param"]["difficulty"] + .1, 1.)
        else: 
            session["param"]["difficulty"] += max(session["param"]["difficulty"] - .2, 0)
        print(f"Current difficulty : {100*session["param"]["difficulty"]}%")

    game_question = query_infos(session["param"])
    msg3 = {"sender": "Agent", "text": game_question.enigma, "class": "ai-message"}
    new_messages.append(msg3)
    history.append(msg3)
    
    session['last_answer'] = game_question.answer
    session['history'] = history
    session.modified = True 
    
    return jsonify(new_messages)
    
if __name__ == '__main__':
    app.run(debug=True)
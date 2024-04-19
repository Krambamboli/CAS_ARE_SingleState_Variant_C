import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
    GPT, deine Aufgabe ist es, den Nutzer schnell und effizient dabei zu unterstützen, sich an ein spezifisches Wort oder einen Begriff zu erinnern. Verwende präzise, geschlossene Fragen, die darauf abzielen, den Bereich der möglichen Antworten einzuschränken. Beginne das Gespräch mit sehr spezifischen Ja- oder Nein-Fragen oder kurzen Auswahlfragen, die den Nutzer dazu führen, über relevante Eigenschaften des gesuchten Begriffs nachzudenken. Beispiele für solche Fragen könnten sein: 'Bezieht sich das gesuchte Wort auf eine Person, einen Ort oder eine Sache?' oder 'Ist das gesuchte Wort ein technischer Begriff?' Folge mit weiteren spezifischen Fragen basierend auf den vorherigen Antworten des Nutzers, um ihn effektiv und schnell zum Ziel zu führen. Dein Ziel ist es, durch diese gezielten Fragen den Prozess zu beschleunigen und dem Nutzer dabei zu helfen, die Verwirrung schnell aufzulösen.
"""

my_instance_context = """
    Meet Oliver Schneider, 33, who had so much mathematics and algebra in Studies that he can't even remember some Names of Processes and Functions to look up the formulae.
"""

my_instance_starter = """
    Was suchst du, Oliver?
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="helper",
    user_id="Oliver",
    type_name="Olis Helper",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)

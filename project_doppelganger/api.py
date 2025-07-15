from flask import Flask, request, jsonify, render_template
from src.main_doppelganger import main as doppelganger_main

app = Flask(__name__)

@app.route('/')
def index():
    """
    Renders the index.html page.
    """
    return render_template('index.html')

@app.route('/interact', methods=['POST'])
def interact():
    """
    An endpoint for interacting with the Doppelganger.
    """
    user_input = request.json['user_input']
    # This is a conceptual integration. In a real implementation,
    # we would have a more sophisticated way of passing the user input
    # to the doppelganger_main function and getting the response.
    response = "This is a dummy response."
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)

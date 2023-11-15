from flask import Flask
from flask_cors import CORS
from flask import Flask, request, jsonify
from scraping import scrape_cookie_policy


app = Flask(__name__)
CORS(app)



@app.route('/')
def hello_world():
    return 'Hello, Cookies!'


@app.route('/get-cookie-policy')
def get_cookie_policy():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Aucun nom de domaine fourni"}), 400

    policy = scrape_cookie_policy(domain)
    return jsonify({"domain": domain, "cookie_policy": policy})

if __name__ == '__main__':
    app.run(debug=True)

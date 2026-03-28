from flask import Flask
from routes.routes import main
from routes.auth_routes import auth

app = Flask(__name__)

app.secret_key = "secret-key"

# register blueprint
app.register_blueprint(main)
app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)
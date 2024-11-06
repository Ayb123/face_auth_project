from flask import Flask, render_template
from login import login_blueprint
from register import register_blueprint

from logout import logout_blueprint

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Changez cela pour une clé secrète plus complexe

# Enregistrement des blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(logout_blueprint)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/welcome/<name>')
def welcome(name):
    return render_template('welcome.html', name=name)




if __name__ == '__main__':
    app.run(debug=True)

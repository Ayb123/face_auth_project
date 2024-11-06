from flask import Blueprint, redirect, url_for, session

logout_blueprint = Blueprint('logout', __name__)

@logout_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    # Supprime toutes les données de session
    session.clear()  # Ou vous pouvez utiliser session.pop('key') pour supprimer une clé spécifique

    # Rediriger vers la page de connexion après la déconnexion
    return redirect(url_for('login.login'))

from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import face_recognition
import shutil
from config import connect_to_database, close_database_connection
import atexit
import hashlib

register_blueprint = Blueprint('register', __name__)

# Connexion à la base de données
db, cursor = connect_to_database()
atexit.register(close_database_connection, db, cursor)

# Formats de fichiers autorisés
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@register_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        birthdate = request.form['birthdate']
        image_file = request.files['image']

        if image_file:
            if not allowed_file(image_file.filename):
                flash("Seuls les fichiers PNG, JPG et JPEG sont autorisés.", "error")
                return render_template('register.html')

            # Nom de fichier unique pour éviter les conflits
            image_filename = f"{name}_{image_file.filename}"
            image_path = os.path.join('images', image_filename)
            image_file.save(image_path)

            if register_user(name, email, password, birthdate, image_path):
                flash("Enregistrement réussi! Veuillez vous connecter.", "success")
                return redirect(url_for('login.login'))
            else:
                # Supprimer l'image temporaire si l'enregistrement échoue
                if os.path.exists(image_path):
                    os.remove(image_path)
                return render_template('register.html')

    return render_template('register.html')

def register_user(name, email, password, birthdate, image_path):
    if not os.path.exists('images'):
        os.makedirs('images')

    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            flash("Aucun visage détecté dans l'image. Veuillez réessayer avec une autre image.", "error")
            return False

        face_encoding = encodings[0]
        face_encoding_blob = face_encoding.tobytes()

        # Hachage du mot de passe pour la sécurité
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        sql = "INSERT INTO users (name, email, password, birthdate, face_encoding) VALUES (%s, %s, %s, %s, %s)"
        values = (name, email, hashed_password, birthdate, face_encoding_blob)
        cursor.execute(sql, values)
        db.commit()

        # Copier l'image dans le dossier final et supprimer l'original si nécessaire
        final_image_path = os.path.join('images', os.path.basename(image_path))
        if image_path != final_image_path:
            shutil.copy(image_path, final_image_path)
            os.remove(image_path)

        return True

    except Exception as e:
        flash(f"Erreur lors de l'enregistrement : {e}", "error")
        return False

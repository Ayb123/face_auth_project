from flask import Blueprint, render_template, request, redirect, url_for, flash
import cv2
import numpy as np
import face_recognition
import hashlib  # For password hashing
from config import connect_to_database, close_database_connection
import atexit

login_blueprint = Blueprint('login', __name__)

# Database connection
db, cursor = connect_to_database()
atexit.register(close_database_connection, db, cursor)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if login is with email/password
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            # Handle email and password authentication
            user_name = authenticate_user_credentials(email, password)
            if user_name:
                flash("Connexion réussie.", "success")
                return redirect(url_for('welcome', name=user_name))  # Utilise le nom de l'utilisateur
            else:
                flash("Identifiant ou mot de passe incorrect.", "error")
        
        else:
            # Handle face recognition authentication
            authenticated_name = authenticate_user_live()
            if authenticated_name:
                return redirect(url_for('welcome', name=authenticated_name))
            else:
                flash("Échec de l'authentification. Veuillez réessayer.", "error")

    return render_template('login.html')


def authenticate_user_credentials(email, password):
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check against the database
    cursor.execute("SELECT name FROM users WHERE email = %s AND password = %s", (email, hashed_password))
    user = cursor.fetchone()

    if user:
        return user[0]  # Return name if authentication succeeds
    return None

def authenticate_user_live():
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        flash("Erreur lors de l'ouverture de la caméra.", "error")
        return None

    attempt_count = 0
    max_attempts = 10
    tolerance_threshold = 0.5

    while attempt_count < max_attempts:
        ret, frame = video_capture.read()
        if not ret:
            flash("Erreur lors de la capture d'image.", "error")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        if face_encodings:
            face_encoding = face_encodings[0]
            cursor.execute("SELECT id, name, face_encoding FROM users")
            users = cursor.fetchall()

            for user in users:
                user_id, user_name, stored_encoding = user
                stored_encoding = np.frombuffer(stored_encoding, dtype=np.float64)
                distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]

                if distance < tolerance_threshold:
                    flash(f"Bienvenue, {user_name}! Identifié avec une distance de {distance:.2f}.", "success")
                    video_capture.release()
                    return user_name

        attempt_count += 1

    flash("Authentification échouée après plusieurs tentatives.", "error")
    video_capture.release()
    return None

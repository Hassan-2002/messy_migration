from flask import request, jsonify, current_app
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

from .db import get_db
from .error import APIError
from .schemas import UserSchema, UserCreateSchema, UserUpdateSchema, LoginSchema

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
login_schema = LoginSchema()

def register_routes(app):
    @app.route('/users', methods=['GET'])
    def get_all_users():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
        return jsonify(users_schema.dump([dict(u) for u in users])), 200

    @app.route('/user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            return jsonify(user_schema.dump(dict(user))), 200
        else:
            raise APIError("User not found", 404)

    @app.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        if not data:
            raise APIError("Request must be JSON", 400)

        try:
            validated_data = user_create_schema.load(data)
        except ValidationError as err:
            raise APIError(message="Validation error", status_code=400, payload=err.messages)

        name = validated_data['name']
        email = validated_data.get('email')
        password = validated_data['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        if cursor.fetchone():
            raise APIError(f"User with name '{name}' already exists", 409)

        if email:
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise APIError(f"Email '{email}' already exists", 409)

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute("INSERT INTO users (name, password_hash, email) VALUES (?, ?, ?)",
                           (name, hashed_password, email))
            db.commit()
            new_user_id = cursor.lastrowid
            return jsonify({"message": "User created successfully", "id": new_user_id}), 201
        except sqlite3.IntegrityError as e:
            current_app.logger.error(f"DB integrity error during user creation: {e}")
            raise APIError("User creation failed due to data conflict.", 409)
        except Exception as e:
            current_app.logger.error(f"Error creating user: {e}")
            raise APIError("Internal server error during user creation", 500)


    @app.route('/user/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        data = request.get_json()
        if not data:
            raise APIError("Request must be JSON", 400)

        try:
            validated_data = user_update_schema.load(data, partial=True)
        except ValidationError as err:
            raise APIError(message="Validation error", status_code=400, payload=err.messages)

        if not validated_data:
            raise APIError("No fields provided for update", 400)

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise APIError("User not found", 404)

        update_fields = []
        update_values = []

        if 'name' in validated_data:
            name = validated_data['name']
            cursor.execute("SELECT id FROM users WHERE name = ? AND id != ?", (name, user_id))
            if cursor.fetchone():
                raise APIError(f"User with name '{name}' already exists", 409)
            update_fields.append("name = ?")
            update_values.append(name)
        if 'email' in validated_data:
            email = validated_data['email']
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                raise APIError(f"Email '{email}' already exists", 409)
            update_fields.append("email = ?")
            update_values.append(email)
        if 'password' in validated_data:
            password = validated_data['password']
            hashed_password = generate_password_hash(password)
            update_fields.append("password_hash = ?")
            update_values.append(hashed_password)

        set_clause = ", ".join(update_fields)
        update_values.append(user_id)

        try:
            cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(update_values))
            db.commit()
            if cursor.rowcount == 0:
                raise APIError("User not found or no changes made", 404)
            return jsonify({"message": "User updated successfully"}), 200
        except sqlite3.IntegrityError as e:
            current_app.logger.error(f"DB integrity error during user update: {e}")
            raise APIError("User update failed due to data conflict.", 409)
        except Exception as e:
            current_app.logger.error(f"Error updating user: {e}")
            raise APIError("Internal server error during user update", 500)


    @app.route('/user/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()

        if cursor.rowcount == 0:
            raise APIError("User not found", 404)
        return '', 204

    @app.route('/search', methods=['GET'])
    def search_users():
        name_query = request.args.get('name')
        if not name_query:
            raise APIError("Name parameter is required for search", 400)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE name LIKE ?", (f"%{name_query}%",))
        users = cursor.fetchall()
        return jsonify(users_schema.dump([dict(u) for u in users])), 200

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data:
            raise APIError("Request must be JSON", 400)

        try:
            validated_data = login_schema.load(data)
        except ValidationError as err:
            raise APIError(message="Validation error", status_code=400, payload=err.messages)

        name = validated_data['name']
        password = validated_data['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, password_hash FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            return jsonify({"message": "Login successful", "user_id": user['id']}), 200
        else:
            raise APIError("Invalid name or password", 401)

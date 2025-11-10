import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from config import SECRET_KEY, JWT_EXP_SECONDS
from models import User

def create_token(user):
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_SECONDS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # PyJWT may return bytes in some versions; ensure string
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def get_jwt_payload(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers.get('Authorization').split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        if not token:
            return jsonify({"message":"Token missing"}), 401
        try:
            payload = get_jwt_payload(token)
            user = User.query.get(payload['sub'])
            if not user:
                return jsonify({"message":"User not found"}), 401
            request.current_user = user
        except Exception as e:
            return jsonify({"message":"Invalid token", "error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        user = request.current_user
        if user.role != 'admin':
            return jsonify({"message":"Forbidden - admin only"}), 403
        return f(*args, **kwargs)
    return decorated

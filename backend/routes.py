from flask import request, jsonify
from session.session_config import SessionConfig


def register_routes(app):

    @app.route("/")
    def home():
        return {
            "message": "AI Customer Support Coaching Assistant Backend Running"
        }


    @app.route("/create-session", methods=["POST"])
    def create_session():

        data = request.get_json()

        session = SessionConfig(**data)

        return jsonify({
            "status": "success",
            "message": "Session Created",
            "session": session.model_dump()
        })
from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.utils.ai_engine import generate_ai_response
from app.models import ChatLog
from app.database import db

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({"success": False, "message": "Message is required."}), 400

    user_name = current_user.name if (current_user.is_authenticated and current_user.name) else "Guest"
    user_phone = current_user.phone if current_user.is_authenticated else "Guest"
    user_location = current_user.location if (current_user.is_authenticated and current_user.location) else "Sarwar, Rajasthan"

    # Generate response from Smart Advisory Engine
    result = generate_ai_response(
        user_message=message,
        user_phone=user_phone,
        user_location=user_location,
        user_name=user_name,
        current_user_obj=current_user if current_user.is_authenticated else None
    )

    # Log Chat to Database
    try:
        chat_log = ChatLog(
            user_phone=user_phone,
            user_location=user_location,
            message=message,
            response=result.get("response", ""),
            matched_plan=result.get("matched_plan")
        )
        db.session.add(chat_log)
        db.session.commit()
    except Exception as e:
        print("Chat logging error recorded.")

    return jsonify({
        "success": True,
        "response": result.get("response"),
        "matched_plan": result.get("matched_plan"),
        "confidence_score": result.get("confidence_score", "95%"),
        "whatsapp_url": result.get("whatsapp_url"),
        "provider_used": result.get("provider_used")
    })

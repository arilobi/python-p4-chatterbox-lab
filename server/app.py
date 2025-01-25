from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

#returning all messages
@app.route('/messages', methods=["GET"])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages])

# creating a new message
@app.route('/messages', methods=["POST"])
def create_message():
    data = request.get_json()

    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return jsonify({"error": "Missing body/username"})
    
    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=["PATCH"])
def messages_by_id(id):
    message = Message.query.get_or_404(id)
    data = request.get_json()

    body = data.get('body')
    if body:
        message.body = body
        db.session.commit()

    return jsonify(message.to_dict())

# Delete a message
@app.route('/messages/<int:id>', methods=["DELETE"])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({"message": "Message deleted"}), 204

# This is to serialize messages
def to_dict(self):
    return {
        "id": self.id,
        "body": self.body,
        "username": self.username,
        "created_at": self.created_at,
        "updated_at": self.updated_at,
    }

# for the message model
Message.to_dict = to_dict

if __name__ == '__main__':
    app.run(port=5555)

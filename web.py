from flask import Flask, request, jsonify
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from models import db, User, ApiData
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)


with app.app_context():
    db.create_all()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({
            'first_name': user.first_name,
            'last_name': user.last_name
        }), 200
    return jsonify({'message': 'Неверный логин или пароль.'}), 401


@app.route('/api/data', methods=['POST'])
def create_api_data():
    data = request.json
    new_data = ApiData(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        start_date=data.get('start_time'),
        end_date=data.get('end_time'),
        total_time=data.get('total_time'),
        results=data.get('results'),
        visited_apps=data.get('visited_apps')
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Данные успешно добавлены!"}), 200


if __name__ == '__main__':
    app.run(debug=True)

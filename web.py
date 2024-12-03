from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, User, ApiData
from config import Config
from Forms import RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'fksdksk$gcdhcbbd%hdicbd'
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
        email=data.get('email'),
        start_date=data.get('start_time'),
        end_date=data.get('end_time'),
        total_time=data.get('total_time'),
        results=data.get('results'),
        visited_apps=data.get('visited_apps')
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Данные успешно добавлены!"}), 200


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Спасибо за регистрацию.', 'success')
        return redirect(url_for('welcome'))
    return render_template('register.html', form=form)


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run(debug=True)

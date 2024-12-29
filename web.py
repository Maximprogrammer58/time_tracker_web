import re
import uuid

from config import Config
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_migrate import Migrate
from Forms import RegistrationForm, RegistrationBossForm, LoginForm
from models import db, User, ApiData, Boss
from werkzeug.security import generate_password_hash, check_password_hash


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
            'last_name': user.last_name,
            'boss_token': user.boss_token
        }), 200
    return jsonify({'message': 'Неверный логин или пароль.'}), 401


@app.route('/api/data', methods=['POST'])
def create_api_data():
    data = request.json
    new_data = ApiData(
        first_name = data.get('first_name'),
        last_name = data.get('last_name'),
        email = data.get('email'),
        start_date = data.get('start_time'),
        end_date = data.get('end_time'),
        total_time = data.get('total_time'),
        results = data.get('results'),
        visited_apps = data.get('visited_apps'),
        boss_token = data.get('boss_token')
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
            password_hash=generate_password_hash(form.password.data),
            boss_token=form.boss_token.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Спасибо за регистрацию.', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)


@app.route('/register_boss', methods=['GET', 'POST'])
def register_boss():
    form = RegistrationBossForm()
    if form.validate_on_submit():
        new_boss = Boss(
            name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password_hash = generate_password_hash(form.password.data),
            unique_token = str(uuid.uuid4())
        )
        db.session.add(new_boss)
        db.session.commit()
        flash('Регистрация успешна! Пожалуйста, войдите.', 'success')
        return redirect(url_for('login_boss'))
    return render_template('register_boss.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def login_boss():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        boss = Boss.query.filter_by(email=email).first()

        if boss and check_password_hash(boss.password_hash, password):
            session['user_id'] = boss.id
            return redirect(url_for('dashboard', id=boss.id))

        flash('Неверный email или пароль', 'error')
    return render_template('login_boss.html', form=form)


def time_to_seconds_v2(time_str):
    pattern = r"(\d+)\s*ч\s*(\d+)\s*мин\s*(\d+)\s*сек"
    match = re.match(pattern, time_str)
    if match:
        hours, minutes, seconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0


@app.route('/dashboard/<int:id>', methods=['GET', 'POST'])
def dashboard(id):
    if 'user_id' not in session or session['user_id'] != id:
        return redirect(url_for('login_boss'))

    boss = Boss.query.get(id)
    api_data_records = ApiData.query.filter_by(boss_token=boss.unique_token).all()
    unique_users = {user.email: user for user in api_data_records}.values()

    selected_email = None
    if request.method == 'POST':
        selected_email = request.form.get('user_email')
        if selected_email:
            api_data_records = [record for record in api_data_records if record.email == selected_email]

    for record in api_data_records:
        total_time_seconds = time_to_seconds_v2(record.total_time)
        if record.results:
            record.results = {
                app: {
                    "time": time_to_seconds_v2(time),
                    "percentage": round((time_to_seconds_v2(time) / total_time_seconds) * 100, 2) if total_time_seconds else 0
                }
                for app, time in record.results.items()
            }

    return render_template(
        'dashboard.html',
        boss=boss,
        users=api_data_records,
        unique_users=unique_users,
        selected_email=selected_email
    )


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_boss'))


if __name__ == '__main__':
    app.run(debug=True)
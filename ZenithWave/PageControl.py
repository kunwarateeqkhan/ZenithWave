from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os


import google.generativeai as genai

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'PabitraMaharana'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.app_context().push()



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')



@app.route("/")
def home():
    return render_template("indexpage/index.html")

@app.route("/chat")
@login_required
def chatpage():
    return render_template("chatpage/chatmain.html")

@app.route('/contentupload')
def fileupload():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('uploadpage/upload.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for('fileupload'))

@app.route("/home")
@login_required
def homeMain():
    return render_template("indexpage/homepage.html")

@app.route('/login', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('homeMain'))
    return render_template("userlogin/signin.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))

    return render_template("userlogin/signup.html", form=form)


@app.route("/videohomepage")
@login_required
def videohome():
    video_files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
    return render_template("videopage/videohome.html", video_files=video_files)


@app.route("/videopage")
@login_required
def video():
    video_files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("videopage/index.html", video_files=video_files, user=user)


@app.route("/listpage")
@login_required
def list():
    audio_files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file.endswith('.mp3')]
    return render_template("audiopage/podcast.html", audio_files=audio_files)

@app.route("/audiopage")
@login_required
def audio():
    return render_template("beatmaker/index.html")

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dash():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("dashboard/dashboard.html", files=files, user=user)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))

@app.route("/get", methods = ["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)


def get_Chat_response(text):
    genai.configure(api_key=)

    # Set up the model
    generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    convo.send_message(text)
    return convo.last.text
 
if __name__ == "__main__":
    app.run(debug=True)
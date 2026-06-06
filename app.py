from flask import (
    Flask,
    render_template,
    redirect,
    request,
    flash,
    url_for
)

from flask_socketio import (
    SocketIO,
    emit,
    join_room

)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_bcrypt import Bcrypt

from werkzeug.utils import secure_filename

from models import db, User, Message

import os
app = Flask(__name__)

app.config["SECRET_KEY"] = "chattr-secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["UPLOAD_FOLDER"] = "static/uploads"

os.makedirs(
    os.path.join(app.config["UPLOAD_FOLDER"], "profile_pics"),
    exist_ok=True
)

db.init_app(app)

bcrypt = Bcrypt(app)

socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))

# HOME

@app.route("/")
def home():

    return redirect(url_for("login")) 

# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")

        email = request.form.get("email")

        password = request.form.get("password")

        user_exits = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()


        if user_exits:

            flash("username or Email already exists")

            return redirect(url_for("register"))
        
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user =User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        flash("Account Created")

        return redirect(url_for("login"))

    return render_template("register.html")    

#LOGIN

@app.route("/login", methods=["GET", "POST"])  
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):
            
            user.online = True

            db.session.commit()

            login_user(user)

            return redirect(url_for("dashboard"))
        
        flash("Invalid credentials")

    return render_template("login.html")    

#LOGOUT 

@app.route("/logout")
@login_required 
def logout():

    current_user.online = False

    db.session.commit()

    return redirect(url_for("login"))

# DashBOARD 

@app.route("/dashboard")
@login_required
def dashboard():

    search = request.args.get("search", "")

    if search:

        users = User.query.filter(
            User.username.ilike(f"%{search}%")
        ).all()

    else:
        users = User.query.all()   

    return render_template(
        "dashboard.html",
        users=users
    )   

# PROFILE 

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method =="POST":

        bio = request.form.get("bio")

        theme = request.form.get("theme")

        current_user.bio = bio

        current_user.theme = theme
        
        file = request.files.get("profile_pic") 
        
        if file and file.filename != "":

            filename = secure_filename(file.filename)

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                "profile_pics",
                filename
            )

            file.save(path)

            current_user.profile_pic = filename

        db.session.commit()    

        flash("profile updated")

    return render_template("profile.html")    

# CHAT 
@app.route("/chat/<int:user_id>")
@login_required
def chat(user_id):

    other_user = User.query.get_or_404(user_id)

    unseen_messages = Message.query.filter_by(
        sender_id=other_user.id,
        receiver_id=current_user.id,
        seen=False
    ).all()

    for msg in unseen_messages:

        msg.seen =True
    db.session.commit()    
    messages =Message.query.filter(
        (
            (Message.sender_id == current_user.id) &
            (Message.receiver_id == other_user.id)
        )

        |

        (
            (Message.sender_id == other_user.id) &
            (Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        "chat.html",
        other_user=other_user,
        messages=messages
    )

# SOCKET JOIN

@socketio.on("join")
def on_join(data):

    room = data["room"]

    join_room(room)

# SEND MESSAGE 
@socketio.on("send_message") 
def handle_send_message(data):

    sender_id = data["sender_id"]

    receiver_id = data["receiver_id"]

    message = data["message"]
    
    room = data["room"]

    new_message =Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=message
    )

    db.session.add(new_message)

    db.session.commit()

    emit(
        "receive_message",
        {
            "sender_id": sender_id,
            "message": message,
            "seen": False
        },
        room=room
    )

# TYPING INDICATOR   

@socketio.on("typing")
def typing(data):

    emit(
        "show_typing",
        data,
        room=data["room"],
        include_self=False
    )

# DATABASE 

with app.app_context():

    db.create_all()   

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
            
        


#used AI assistance (Claude)
from flask import Flask , render_template , request , redirect , session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL
from datetime import datetime
from dotenv import load_dotenv
import os
import re
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
def apology(n):
    return render_template("apology.html", n = n)


app = Flask(__name__)     
db = SQL("sqlite:///chess.db")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['DEBUG'] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')



@app.route("/progress")
@login_required
def progress():
    date_rating = db.execute("SELECT date ,user_rating  FROM games WHERE user_id = ? ORDER BY date ASC",session.get("user_id"))
    return render_template("progress.html" , date_rating = date_rating )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("Username"):
            return apology("Must provide name")
        user_name = request.form.get("Username")
        if not request.form.get("Password"):
            return apology("Must provide password")
        password = request.form.get("Password")
        if password != request.form.get("Confirmation"):
            return apology("Passwords must match")
        
        pattern = r"^.{8,}$"
        if re.match(pattern, password):
            row = db.execute("SELECT user_name FROM users WHERE user_name = ?", user_name )
            if len(row) != 0:
                return apology("Username is taken")
            hashed_password = generate_password_hash(password)
            user_id = db.execute("INSERT INTO users (user_name, hash) VALUES (?,?)",user_name , hashed_password)
            session["user_id"]= user_id
            return redirect("/")
        else:
            return apology("Passwords dose not match the rules")
    else:
        return render_template("register.html")
    


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("Username"):
            return apology("Must provide name")
        
        user_name = request.form.get("Username")

        if not request.form.get("Password"):
            return apology("Must provide password")
        
        rows = db.execute("SELECT user_id, hash FROM users WHERE user_name = ?",user_name )
        if len(rows) == 1 and check_password_hash(rows[0]["hash"],request.form.get("Password")):
            session["user_id"] = rows[0]["user_id"]
            return redirect("/")
        else:
            return apology("Password or username invalid")
    

    else:
        return render_template("login.html")




@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/", methods = ["GET", "POST"])
@login_required
def home():
    #win rate by color
    id = session.get("user_id")
    total_games_white = db.execute("SELECT COUNT(result), color FROM games WHERE user_id = ? and color = ?", id, "white" )
    total_games_black = db.execute("SELECT COUNT(result), color FROM games WHERE user_id = ? and color = ?", id, "black" )

    wins_white = db.execute("SELECT COUNT(result),color FROM games WHERE user_id = ? AND result = ? AND color = ?", id, "win" , "white" )
    wins_black = db.execute("SELECT COUNT(result),color FROM games WHERE user_id = ? AND result = ? AND color = ?",id, "win" , "black" )

    try:
        win_rate =  (wins_white[0]["COUNT(result)"] + wins_black[0]["COUNT(result)"]) / (total_games_white[0]["COUNT(result)"] + total_games_black[0]["COUNT(result)"])
    except:
        win_rate = 0
    try:
        win_rate_black =  wins_black[0]["COUNT(result)"] / total_games_black[0]["COUNT(result)"] 
    except:
        win_rate_black = 0
    try:
        win_rate_white =  wins_white[0]["COUNT(result)"] / total_games_white[0]["COUNT(result)"] 
    except:
        win_rate_white = 0
    #win rate by opening
    opening_win = db.execute("SELECT COUNT(result), opening FROM games WHERE user_id = ? AND result = ? GROUP BY opening", id , "win")
    opening_games = db.execute("SELECT COUNT(result), opening FROM games WHERE user_id = ?  GROUP BY opening", id)
    wins_per_opining = {}
    games_per_opining = {}
    opening_win_rates = {}

    for i in opening_win:
         wins_per_opining[i["opening"]] =  i["COUNT(result)"]

    for i in opening_games:
     if i["COUNT(result)"] > 2:
         games_per_opining[i["opening"]] =  i["COUNT(result)"]

    

    for i in games_per_opining:
        opening_win_rates[i] = (wins_per_opining.get(i, 0) / games_per_opining[i])

    return render_template("home.html" , opening_win_rates= opening_win_rates, win_rate = win_rate, win_rate_black =win_rate_black, win_rate_white= win_rate_white)

     

@app.route("/add", methods = ["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        color = request.form.get("color")
        result = request.form.get("result")
        opening = request.form.get("opening")
        opponent_rating = request.form.get("opponent_rating")
        user_rating = request.form.get("user_rating")
        date = request.form.get("date")

        if color not in ["white","black"]:
            return apology("ivalid color")

        if result not in ["win","loss","draw"]:
            return apology("Result is invalid")
        
        try:
            opponent_rating = int(opponent_rating)
        except:
            return apology("Opponent rating is invalid")
        if opponent_rating <= 0:
            return apology("Opponent rating is invalid")
        try: 
            user_rating = int(user_rating)
        except:
            return apology("You'r rating is invalid")
        if user_rating <= 0:
            return apology("You'r rating is invalid")
        if not opening:
            return apology("Opening is invalid")
        
        date_format = "%Y-%m-%d"
        try:
            datetime.strptime(date, date_format)
        except ValueError:
            return apology("Date is invalid")

        
        db.execute("INSERT INTO games (user_id , date, color, result, opening, opponent_rating, user_rating) VALUES (?,?,?,?,?,?,?)",session.get("user_id") ,date ,color ,result ,opening ,opponent_rating ,user_rating )
        return redirect("/")
    else:
        return render_template("add.html")



@app.route("/history")
@login_required
def history():
        game_history = db.execute("SELECT * FROM games WHERE user_id = ? ORDER BY date DESC",session.get("user_id"))
        return render_template("history.html", game_history = game_history )


@app.route("/edit/<int:id>", methods = ["POST", "GET"])
@login_required
def edit(id):
    if request.method == "POST":
        user_id = session.get("user_id")

        game_info = db.execute("SELECT * FROM games WHERE id = ?",id )
        if not game_info[0]["user_id"] == user_id:
            return apology("This game dose not belong to you")

        color = request.form.get("color")
        result = request.form.get("result")
        opening = request.form.get("opening")
        opponent_rating = request.form.get("opponent_rating")
        user_rating = request.form.get("user_rating")
        date = request.form.get("date")

        if color not in ["white","black"]:
            return apology("ivalid color")

        if result not in ["win","loss","draw"]:
            return apology("Result is invalid")
        
        try:
            opponent_rating = int(opponent_rating)
        except:
            return apology("Opponent rating is invalid")
        try: 
            user_rating = int(user_rating)
        except:
            return apology("You'r rating is invalid")
        
        if not opening:
            return apology("Opening is invalid")
        
        date_format = "%Y-%m-%d"
        try:
            datetime.strptime(date, date_format)
        except ValueError:
            return apology("Date is invalid")
        
        db.execute("UPDATE games SET date = ?, color = ?, result = ?, opening = ?, opponent_rating = ?, user_rating = ? WHERE user_id = ? AND id = ?" , date,color,result,opening,opponent_rating,user_rating,user_id , id)
        return redirect("/history")
    else:
        game_info = db.execute("SELECT * FROM games WHERE id = ?",id )
        if game_info[0]["user_id"] == session.get("user_id"):
            return render_template("edit.html",game_info = game_info ,id = id)
        else:
            return apology("This game dose not belong to you")


@app.route("/delete/<int:id>", methods = ["POST"])
@login_required
def delete(id):
    game_info = db.execute("SELECT * FROM games WHERE id = ?",id )
    if game_info[0]["user_id"] == session.get("user_id"):
        db.execute("DELETE FROM games WHERE id = ?", id)
        return redirect("/history")
    else:
        return apology("This game does not belong to you")




from flask import Flask, render_template, request, session
from flask import Flask, render_template, request
import pickle
import sqlite3

app = Flask(__name__)
app.secret_key = "diabetes_secret_key"

with open("models/diabetes_model.pkl", "rb") as f:
    model = pickle.load(f)
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return "Please Login First"

    conn = sqlite3.connect("database/diabetes.db")
    cursor = conn.cursor()

    # KPI Cards
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM predictions
    WHERE prediction='Diabetic'
    """)
    diabetic = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(probability) FROM predictions")
    avg_risk = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(probability) FROM predictions")
    max_risk = cursor.fetchone()[0] or 0
    conn.close()
    # Pie Chart Data
    non_diabetic = total - diabetic

    return render_template(
        "dashboard.html",
        total=total,
        diabetic=diabetic,
        non_diabetic=non_diabetic,
        avg_risk=round(avg_risk,2),
        max_risk=round(max_risk,2)
    )
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():

    if "user_id" not in session:
        return "Please Login First"
    data = [
        float(request.form["Pregnancies"]),
        float(request.form["Glucose"]),
        float(request.form["BloodPressure"]),
        float(request.form["SkinThickness"]),
        float(request.form["Insulin"]),
        float(request.form["BMI"]),
        float(request.form["DiabetesPedigreeFunction"]),
        float(request.form["Age"])
    ]

    prediction = model.predict([data])[0]

    probability = model.predict_proba([data])[0][1]

    result = "Diabetic" if prediction == 1 else "Non-Diabetic"

    conn = sqlite3.connect("database/diabetes.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions
    (user_id, age, glucose, probability, prediction)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        session["user_id"],
        data[7],          # Age
        data[1],          # Glucose
        probability * 100,
        result
    ))

    conn.commit()
    conn.close()
    return render_template(
        "index.html",
        prediction=result,
        probability=round(probability * 100, 2)
    )
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database/diabetes.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username=? AND password=?
            """,
            (username,password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = username
            session["user_id"] = user[0]

            return "Login Successful"

        return "Invalid Credentials"

    return render_template("login.html")
@app.route("/history")
def history():

    if "user_id" not in session:
        return "Please Login First"

    conn = sqlite3.connect("database/diabetes.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, age, glucose, probability,
        prediction, created_at
    FROM predictions
    WHERE user_id=?
    ORDER BY id DESC
    """, (session["user_id"],))

    records = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database/diabetes.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return "Registration Successful"

    return render_template("register.html")
if __name__ == "__main__":
    app.run(debug=True)
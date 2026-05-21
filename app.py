from flask import Flask, render_template, request, redirect, session
from db import base, engine, sessionLocal
import models
import PyPDF2
import docx
import json

app = Flask(__name__)
app.secret_key = "Secret123"

# Create Tables
base.metadata.create_all(bind=engine)


# ---------------- AI Function ----------------
def analyze_resume(resume, role):

    return {
        "skills": [
            "Python",
            "Flask",
            "SQL"
        ],

        "missing_skills": [
            "Docker",
            "AWS"
        ],

        "roadmap": [
            "Learn Docker",
            "Build Flask APIs",
            "Learn AWS Basics"
        ],

        "interview_questions": [
            "Explain Flask routing",
            "What is SQLAlchemy?",
            "Difference between GET and POST?"
        ]
    }


# ---------------- Home Route ----------------
@app.route("/")
def home():

    if "user" in session:
        return redirect("/dashboard")

    return redirect("/login")


# ---------------- Signup ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

    db = sessionLocal()

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(
            email=email
        ).first()

        if existing_user:
            return "User already exists"

        user = models.User(
            email=email,
            password=password
        )

        db.add(user)
        db.commit()

        return redirect("/login")

    return render_template("signup.html")


# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    db = sessionLocal()

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session["user"] = user.email

            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template("login.html")


# ---------------- Dashboard ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        # ---------- File Handling ----------
        if file and file.filename != "":

            # PDF File
            if file.filename.endswith(".pdf"):

                try:

                    pdf_reader = PyPDF2.PdfReader(file)

                    text = ""

                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""

                    resume_text = text

                except Exception as e:

                    result = {
                        "error": f"PDF error: {str(e)}"
                    }

            # DOCX File
            elif file.filename.endswith(".docx"):

                try:

                    doc = docx.Document(file)

                    text = ""

                    for para in doc.paragraphs:
                        text += para.text + "\n"

                    resume_text = text

                except Exception as e:

                    result = {
                        "error": f"DOCX error: {str(e)}"
                    }

        # ---------- Resume Analysis ----------
        if resume_text and user_goal:

            try:

                result = analyze_resume(
                    resume_text,
                    user_goal
                )

                # Save Report in Database
                db = sessionLocal()

                user = db.query(models.User).filter_by(
                    email=session["user"]
                ).first()

                report = models.Report(
                    user_id=user.id,
                    resume_text=resume_text,
                    results=json.dumps(result)
                )

                db.add(report)
                db.commit()

            except Exception as e:

                result = {
                    "error": f"AI error: {str(e)}"
                }

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )


# ---------------- History ----------------
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    db = sessionLocal()

    user = db.query(models.User).filter_by(
        email=session["user"]
    ).first()

    reports = db.query(models.Report).filter_by(
        user_id=user.id
    ).all()

    parsed_reports = []

    # Convert JSON String to Dictionary

    parsed_reports=[]
    for r in reports:

        try:
            parsed_result = json.loads(r.results)

        except:
            parsed_result = {}

        parsed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })

    return render_template(
        "history.html",
        reports=parsed_reports
    )


# ---------------- Logout ----------------
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
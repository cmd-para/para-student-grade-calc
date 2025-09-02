from flask import Flask, render_template, request, session
import math

app = Flask(__name__)
app.secret_key = "pogijosh123"  # Required for session storage


def compute_term(absences, exam, quizzes, reqs, reci, term_name):
    # Absence rule
    if absences >= 4:
        return 0, f"{term_name}: FAILED due to absences"

    # Attendance (max 100, min 0)
    attendance = max(0, 100 - (absences * 10))

    # Class Standing = 40% quizzes + 30% requirements + 30% recitation
    class_standing = (quizzes * 0.40) + (reqs * 0.30) + (reci * 0.30)

    # Term Grade = 60% Exam + 10% Attendance + 30% Class Standing
    term_grade = (exam * 0.60) + (attendance * 0.10) + (class_standing * 0.30)

    return term_grade, f"{term_name} Grade: {term_grade:.2f}"


@app.route("/", methods=["GET", "POST"])
def index():
    prelim = midterm = finals = overall = None
    req_mid_pass = req_mid_dl = None
    req_fin_pass = req_fin_dl = None

    if request.method == "POST":
        action = request.form["action"]

        # PRELIM
        if action == "prelim":
            grade, msg = compute_term(
                int(request.form["prelim_abs"]),
                float(request.form["prelim_exam"]),
                float(request.form["prelim_quiz"]),
                float(request.form["prelim_reqs"]),
                float(request.form["prelim_reci"]),
                "Prelim"
            )
            prelim = msg
            session["prelim"] = grade

            # Required Midterm and Finals (assuming = 75 for pass, 90 for DL)
            req_mid_pass = math.ceil((75 - (0.20 * grade) - (0.50 * 75)) / 0.30)
            req_mid_dl = math.ceil((90 - (0.20 * grade) - (0.50 * 90)) / 0.30)

            req_fin_pass = math.ceil((75 - (0.20 * grade) - (0.30 * 75)) / 0.50)
            req_fin_dl = math.ceil((90 - (0.20 * grade) - (0.30 * 90)) / 0.50)

        # MIDTERM
        elif action == "midterm":
            grade, msg = compute_term(
                int(request.form["mid_abs"]),
                float(request.form["mid_exam"]),
                float(request.form["mid_quiz"]),
                float(request.form["mid_reqs"]),
                float(request.form["mid_reci"]),
                "Midterm"
            )
            midterm = msg
            session["midterm"] = grade

            prelim_val = session.get("prelim", 0)

            # Required Finals for pass/DL
            req_fin_pass = math.ceil((75 - (0.20 * prelim_val) - (0.30 * grade)) / 0.50)
            req_fin_dl = math.ceil((90 - (0.20 * prelim_val) - (0.30 * grade)) / 0.50)

        # FINALS
        elif action == "finals":
            grade, msg = compute_term(
                int(request.form["fin_abs"]),
                float(request.form["fin_exam"]),
                float(request.form["fin_quiz"]),
                float(request.form["fin_reqs"]),
                float(request.form["fin_reci"]),
                "Finals"
            )
            finals = msg
            session["finals"] = grade

        # OVERALL
        elif action == "overall":
            prelim_val = session.get("prelim", 0)
            mid_val = session.get("midterm", 0)
            fin_val = session.get("finals", 0)

            if prelim_val == 0 and mid_val == 0 and fin_val == 0:
                overall = "Please calculate Prelim, Midterm, and Finals first."
            else:
                overall_score = (0.20 * prelim_val) + (0.30 * mid_val) + (0.50 * fin_val)

                if overall_score < 75:
                    overall = f"Overall Grade: {overall_score:.2f} - FAILED"
                elif overall_score < 90:
                    overall = f"Overall Grade: {overall_score:.2f} - PASSED"
                else:
                    overall = f"Overall Grade: {overall_score:.2f} - DEAN'S LISTER"
                    
        elif action == "reset":
            session.clear()

    return render_template(
        "index.html",
        prelim=prelim,
        midterm=midterm,
        finals=finals,
        overall=overall,
        req_mid_pass=req_mid_pass,
        req_mid_dl=req_mid_dl,
        req_fin_pass=req_fin_pass,
        req_fin_dl=req_fin_dl
    )


if __name__ == "__main__":
    app.run(debug=True)

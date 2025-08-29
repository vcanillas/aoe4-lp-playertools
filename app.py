from flask import Flask, render_template
from controllers import home_bp, admin_bp, draft_bp, tournament_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(draft_bp)
app.register_blueprint(tournament_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

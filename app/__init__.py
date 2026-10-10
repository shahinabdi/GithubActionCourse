import os
import sqlite3

from flask import Flask, g, jsonify, redirect, render_template, request, url_for


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "todos.db")
    app.config["APP_VERSION"] = os.environ.get("APP_VERSION", "dev")

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        get_db().execute(
            "CREATE TABLE IF NOT EXISTS todos ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)"
        )
        get_db().commit()

    @app.get("/")
    def index():
        todos = get_db().execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
        return render_template("index.html", todos=todos, version=app.config["APP_VERSION"])

    @app.post("/add")
    def add():
        title = request.form.get("title", "").strip()
        if title:
            get_db().execute("INSERT INTO todos (title) VALUES (?)", (title,))
            get_db().commit()
        return redirect(url_for("index"))

    @app.post("/toggle/<int:todo_id>")
    def toggle(todo_id: int):
        get_db().execute("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
        get_db().commit()
        return redirect(url_for("index"))

    @app.post("/delete/<int:todo_id>")
    def delete(todo_id: int):
        get_db().execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        get_db().commit()
        return redirect(url_for("index"))

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=app.config["APP_VERSION"])

    return app

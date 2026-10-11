import os
import sqlite3

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class Todo(BaseModel):
    id: int
    title: str
    done: bool


def create_api_app(db_path: str | None = None) -> FastAPI:
    database_path = db_path or os.environ.get("DB_PATH", "todos.db")
    environment = os.environ.get("APP_ENV", "dev")
    version = os.environ.get("APP_VERSION", "dev")
    app = FastAPI(title="Todo API", version=version)

    def connect() -> sqlite3.Connection:
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        return connection

    with connect() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS todos ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)"
        )

    def serialize(row: sqlite3.Row) -> Todo:
        return Todo(id=row["id"], title=row["title"], done=bool(row["done"]))

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": environment, "version": version}

    @app.get("/api/v1/todos", response_model=list[Todo])
    def list_todos() -> list[Todo]:
        with connect() as connection:
            rows = connection.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
        return [serialize(row) for row in rows]

    @app.post(
        "/api/v1/todos",
        response_model=Todo,
        status_code=status.HTTP_201_CREATED,
    )
    def create_todo(todo: TodoCreate) -> Todo:
        title = todo.title.strip()
        if not title:
            raise HTTPException(status_code=422, detail="Title must not be blank")
        with connect() as connection:
            cursor = connection.execute(
                "INSERT INTO todos (title) VALUES (?)", (title,)
            )
            row = connection.execute(
                "SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=500, detail="Todo was not created")
        return serialize(row)

    @app.patch("/api/v1/todos/{todo_id}/toggle", response_model=Todo)
    def toggle_todo(todo_id: int) -> Todo:
        with connect() as connection:
            connection.execute(
                "UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,)
            )
            row = connection.execute(
                "SELECT * FROM todos WHERE id = ?", (todo_id,)
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return serialize(row)

    @app.delete("/api/v1/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_todo(todo_id: int) -> None:
        with connect() as connection:
            cursor = connection.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")

    return app

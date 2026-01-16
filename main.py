# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# app = FastAPI(title='To-Do-Serv')

# class Task(BaseModel):
#     title: str
#     completed: bool = False

# # Имитация БД
# tasks = {} # Пустой словарь с тасками
# # 'task1': ['Сделать ДЗ по ПИ', True]
# task_id_counter = 1
# # POST /items: создание задачи
# @app.post("/tasks")
# def create_task(task: Task):
#     global task_id_counter
#     tasks[task_id_counter] = task
#     task_id_counter += 1
#     return {"id": task_id_counter - 1, "task": task}

# # GET /tasks - получение списка всех задач
# @app.get("/tasks")
# def get_all_tasks():
#     return {"tasks": tasks}
# # GET /tasks/{id} - получение информации о конкретной задаче
# @app.get("/tasks/{task_id}")
# def get_task(task_id: int):
#     if task_id not in tasks: # Есть ли задача с таким ID?
#         return HTTPException(status_code=404, detail="Task not found")
#     return tasks [task_id]

# # PUT /tasks/{id} - обновление задачи (изменение текста или статуса)
# @app.put("/tasks/{task_id}")
# def update_task(task_id: int, updated_task: Task):
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task for update not found")
#     tasks[task_id] = updated_task
#     return {"id": task_id, "task": updated_task}

# # DELETE /tasks/{id} - удаление задачи
# @app.delete("/tasks/{task_id}")
# def delete_task(task_id: int):
#     if task_id not in tasks:
#         raise HTTPException(satus_code=404, detail="Task for delete not found")
#     del tasks[task_id]
#     return {"status": "deleted"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import string, random
from fastapi.responses import RedirectResponse
import sqlite3
import string, random

app = FastAPI(title='URL Shorter with SQLite')

# Модель для POST запроса
class URLItem(BaseModel):
    url: str

# Подключение к SQLITE
conn = sqlite3.connect("urls.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS urls (
    short_id TEXT PRIMARY KEY,
    full_url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0
)
""")
conn.commit()

# Генератор короткого ID

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(chars) for _ in range(length))
        cur.execute("SELECT 1 FROM urls WHERE short_id = ?", (short_id,))
        if cur.fetchone() is None:
            return short_id
        
# POST shorten
        
@app.post("/shorten")
def shorten_url(item: URLItem):
    short_id = generate_short_id()
    cur.execute(
        "INSERT INTO urls (short_id, full_url, clicks) VALUES (?, ?, ?)",
        (short_id, item.url, 0)
    )
    conn.commit()
    return {"short_url": f"http://127.0.0.1:8000/{short_id}"}

# GET short_id

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    cur.execute("SELECT full_url, clicks FROM urls WHERE short_id = ?", (short_id,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    full_url, clicks = row
    clicks += 1
    cur.execute("UPDATE urls SET clicks = ? WHERE short_id = ?", (clicks, short_id))
    conn.commit()
    return RedirectResponse(full_url)

# ===== GET /stats/{short_id} =====
@app.get("/stats/{short_id}")
def get_stats(short_id: str):
    cur.execute("SELECT full_url, clicks FROM urls WHERE short_id = ?", (short_id,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    full_url, clicks = row
    return {"url": full_url, "clicks": clicks}

    
     
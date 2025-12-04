from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

@app.get("/")
async def root():
    return {"data": "hello world"}

class Blog(BaseModel):
    title: str
    content: str
    author: str
    published: Optional[bool] = False

blogs_db = []

@app.post("/blogs")
def create_post(blog: Blog):
    blogs_db.append(blog.dict())
    return {
        "message": "Blog created successfully",
        "data": blog,
        "blog_id": len(blogs_db) - 1
    }

@app.get("/blogs")
def get_all_blogs():
    return {"blogs": blogs_db}

@app.get("/blogs/{blog_id}")
def get_blog(blog_id: int):
    if blog_id < 0 or blog_id >= len(blogs_db):
        return {"error": "Blog not found"}
    return {"blog": blogs_db[blog_id]}
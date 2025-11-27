from fastapi import FastAPI, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from math import ceil

app = FastAPI(
    title="Book Management API",
    description="یک سیستم مدیریت کتاب‌ها با قابلیت CRUD، جستجو و فیلتر",
    version="1.0.0"
)

# دیتابیس موقت در حافظه
books_db = []
current_id = 1

# مدل‌های Pydantic
class BookCreate(BaseModel):
    title: str
    author: str
    publication_year: int

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publication_year: Optional[int] = None

class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    books: List[BookResponse]

# توابع کمکی
def find_book(book_id: int):
    """پیدا کردن کتاب بر اساس ID"""
    for book in books_db:
        if book["id"] == book_id:
            return book
    return None

def get_book_index(book_id: int):
    """پیدا کردن ایندکس کتاب بر اساس ID"""
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            return index
    return -1

# Endpoints
@app.post("/books/", response_model=BookResponse, status_code=201)
async def create_book(book: BookCreate):
    """افزودن کتاب جدید"""
    global current_id
    
    new_book = {
        "id": current_id,
        "title": book.title,
        "author": book.author,
        "publication_year": book.publication_year
    }
    
    books_db.append(new_book)
    current_id += 1
    
    return new_book

@app.get("/books/", response_model=PaginatedResponse)
async def get_books(
    page: int = Query(1, ge=1, description="شماره صفحه"),
    size: int = Query(10, ge=1, le=100, description="تعداد آیتم در صفحه"),
    title: Optional[str] = Query(None, description="جستجو در عنوان"),
    author: Optional[str] = Query(None, description="جستجو در نویسنده"),
    year: Optional[int] = Query(None, description="فیلتر بر اساس سال انتشار")
):
    """دریافت لیست کتاب‌ها با قابلیت pagination، جستجو و فیلتر"""
    
    # فیلتر کردن کتاب‌ها
    filtered_books = books_db.copy()
    
    if title:
        filtered_books = [book for book in filtered_books if title.lower() in book["title"].lower()]
    
    if author:
        filtered_books = [book for book in filtered_books if author.lower() in book["author"].lower()]
    
    if year:
        filtered_books = [book for book in filtered_books if book["publication_year"] == year]
    
    # محاسبات pagination
    total = len(filtered_books)
    total_pages = ceil(total / size) if total > 0 else 1
    
    # محدود کردن صفحه
    if page > total_pages:
        raise HTTPException(status_code=400, detail="صفحه مورد نظر وجود ندارد")
    
    # برش دادن نتایج برای صفحه جاری
    start_index = (page - 1) * size
    end_index = start_index + size
    paginated_books = filtered_books[start_index:end_index]
    
    return {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": total_pages,
        "books": paginated_books
    }

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    """دریافت اطلاعات یک کتاب خاص"""
    book = find_book(book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="کتاب مورد نظر یافت نشد")
    
    return book

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book_update: BookUpdate):
    """ویرایش اطلاعات کتاب"""
    book_index = get_book_index(book_id)
    
    if book_index == -1:
        raise HTTPException(status_code=404, detail="کتاب مورد نظر یافت نشد")
    
    # به‌روزرسانی فیلدها
    updated_book = books_db[book_index].copy()
    
    if book_update.title is not None:
        updated_book["title"] = book_update.title
    
    if book_update.author is not None:
        updated_book["author"] = book_update.author
    
    if book_update.publication_year is not None:
        updated_book["publication_year"] = book_update.publication_year
    
    books_db[book_index] = updated_book
    
    return updated_book

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    """حذف کتاب"""
    book_index = get_book_index(book_id)
    
    if book_index == -1:
        raise HTTPException(status_code=404, detail="کتاب مورد نظر یافت نشد")
    
    deleted_book = books_db.pop(book_index)
    
    return {
        "message": "کتاب با موفقیت حذف شد",
        "deleted_book": deleted_book
    }

@app.get("/")
async def root():
    """صفحه اصلی"""
    return {
        "message": "به سیستم مدیریت کتاب‌ها خوش آمدید!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# اضافه کردن داده‌های نمونه
@app.on_event("startup")
async def startup_event():
    """اضافه کردن چند کتاب نمونه هنگام راه‌اندازی سرور"""
    sample_books = [
        {"title": "Python Crash Course", "author": "Eric Matthes", "publication_year": 2019},
        {"title": "Fluent Python", "author": "Luciano Ramalho", "publication_year": 2015},
        {"title": "Clean Code", "author": "Robert C. Martin", "publication_year": 2008},
        {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "publication_year": 1999},
        {"title": "Design Patterns", "author": "Erich Gamma", "publication_year": 1994},
        {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "publication_year": 2009},
        {"title": "Deep Learning", "author": "Ian Goodfellow", "publication_year": 2016},
        {"title": "You Don't Know JS", "author": "Kyle Simpson", "publication_year": 2015},
        {"title": "The Rust Programming Language", "author": "Steve Klabnik", "publication_year": 2018},
        {"title": "Effective Java", "author": "Joshua Bloch", "publication_year": 2018}
    ]
    
    global current_id
    for book in sample_books:
        books_db.append({
            "id": current_id,
            "title": book["title"],
            "author": book["author"],
            "publication_year": book["publication_year"]
        })
        current_id += 1

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
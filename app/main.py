from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import app.crud as crud
import app.schemas as schemas
from app.database import get_db
from app.parser_service import ParserService

app = FastAPI(title="Wildberries Parser API", version="1.0.0")

parsing_status = {"is_parsing": False, "progress": "Готов"}


@app.get("/")
def read_root():
    return {"message": "Wildberries Parser API"}


@app.get("/products/", response_model=List[schemas.Product])
def read_products(
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = Query(None, description="Поиск по названию или бренду"),
        db: Session = Depends(get_db)
):
    """Получить все товары с возможностью поиска"""
    return crud.get_products(db, skip=skip, limit=limit, search=search)


@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Добавить товар вручную"""
    return crud.create_product(db=db, product=product)


@app.post("/parse/")
def parse_products(
        query: str,
        pages: int = Query(1, ge=1, le=100, description="Количество страниц для парсинга"),
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db)
):
    """Запустить парсинг товаров с Wildberries"""
    global parsing_status

    if parsing_status["is_parsing"]:
        raise HTTPException(status_code=400, detail="Парсинг уже выполняется")

    parsing_status["is_parsing"] = True
    parsing_status["progress"] = "Начинаем парсинг..."

    def run_parsing():
        try:
            service = ParserService(db)
            results = service.parse_and_save_search(query, pages)
            parsing_status.update({
                "is_parsing": False,
                "progress": "Завершено",
                "last_results": results
            })
        except Exception as e:
            parsing_status.update({
                "is_parsing": False,
                "progress": f"Ошибка: {str(e)}"
            })

    if background_tasks:
        background_tasks.add_task(run_parsing)
        return {
            "message": f"Парсинг запущен в фоне для запроса: '{query}'",
            "pages": pages,
            "status": "processing"
        }
    else:
        service = ParserService(db)
        results = service.parse_and_save_search(query, pages)
        parsing_status["is_parsing"] = False

        return {
            "message": f"Парсинг завершен для запроса: '{query}'",
            "results": results
        }


@app.get("/parse/status")
def get_parsing_status():
    """Получить статус парсинга"""
    return parsing_status

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удалить товар"""
    db_product = crud.delete_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
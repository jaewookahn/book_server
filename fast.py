from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse
import urllib.parse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/books/{book_path:path}")
def get_book(book_path):
    file_root = '/data/'
    book_path_decoded = urllib.parse.unquote_plus(book_path)
    file_path = f'{file_root}/{book_path_decoded}'
    #return {'file_path': file_path, 'original': book_path}
    return FileResponse(file_path)

@app.get("/file/{path}")
async def get_file(path):
    some_file_path = f'/data/{path}'
    return FileResponse(some_file_path)

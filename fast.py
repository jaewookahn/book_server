from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse
import urllib.parse
from ebooklib import epub
import ebooklib
from starlette.responses import StreamingResponse
import io

app = FastAPI()

def get_cover(file_path):
    book = epub.read_epub(file_path)

    images = [image for image in book.get_items_of_type(ebooklib.ITEM_IMAGE)]
    found = images[0]
    for image in images:
        if image.file_name.find('cover') >= 0:
            found = image
            break
    return image

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
    cover_image = get_cover(file_path)

    return StreamingResponse(io.BytesIO(cover_image.content), media_type="image/jpg")

@app.get("/file/{path}")
async def get_file(path):
    some_file_path = f'/data/{path}'
    return FileResponse(some_file_path)

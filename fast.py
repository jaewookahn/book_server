from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import urllib.parse

from ebooklib import epub
import ebooklib
import io
from PIL import Image

app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
        )


def get_cover(file_path):
    book = epub.read_epub(file_path)

    images = [image for image in book.get_items_of_type(ebooklib.ITEM_IMAGE)]
    found = images[0]
    for image in images:
    #for item in book.items:
    #    if item.get_type() == ebooklib.ITEM_DOCUMENT:
    #        continue

        #if 'cover' in str(image.get_type()):
        if image.file_name.find('cover') >= 0:
            found = image
            break
    return image

def get_book_file_path(book_path):
    file_root = '/data/'
    book_path_decoded = urllib.parse.unquote_plus(book_path, encoding='utf-8', errors='replace')
    book_path_decoded = book_path_decoded.replace('volume2', '')
    file_path = f'{file_root}/{book_path_decoded}'
    return file_path

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/books/cover/{book_path:path}")
def get_book_cover(book_path):
    file_path = get_book_file_path(book_path)
    cover_image = get_cover(file_path)
    
    image_type = cover_image.file_name.split('.')[-1]
    return StreamingResponse(io.BytesIO(cover_image.content), media_type=f"image/{image_type}")

@app.get('/books/thumbnail/{book_path:path}')
def get_book_cover_thumbnail(book_path):
    file_path = get_book_file_path(book_path)
    cover_image = get_cover(file_path)

    pimg = Image.open(io.BytesIO(cover_image.content))
    pimg.thumbnail((100,100))
    with io.BytesIO() as output:
        pimg.save(output, format='png')
        pcontents = output.getvalue()

    return StreamingResponse(io.BytesIO(pcontents), media_type='image/png')
 
@app.get("/file/{path}")
async def get_file(path):
    some_file_path = f'/data/{path}'
    return FileResponse(some_file_path)

@app.get('/books/file/{book_path:path}')
def get_book_file(book_path):
    file_path = get_book_file_path(book_path)
    return FileResponse(file_path)

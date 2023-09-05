from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import urllib.parse

from ebooklib import epub
import ebooklib
import io
from PIL import Image
import gc
import copy

app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
        )

def get_cover(file_path):

    try:
        book = epub.read_epub(file_path)
    except:
        return open('book-small-error.png', 'rb').read(), 'cover-error.png'

    images = [image for image in book.get_items_of_type(ebooklib.ITEM_IMAGE)]

    if len(images) == 0:
        return open('book-small.png', 'rb').read(), 'cover-small.png'

    found = None
    for image in images:
        if image.file_name.find('cover') >= 0:
            found = image
            break

    if not found:
        try:
            cover_id = book.metadata['http://www.idpf.org/2007/opf']['cover'][0][1]['content']
        except:
            cover_id = ''
        
        for image in images:
            if image.id == cover_id:
                found = image
                break

    if not found:
        found = images[0]

    cover_content = copy.deepcopy(found.content)
    cover_file_name = copy.deepcopy(found.file_name)

    del found
    del images
    del book

    return cover_content, cover_file_name

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
async def get_book_cover(book_path):
    file_path = get_book_file_path(book_path)
    cover_image_content, cover_image_file_name = get_cover(file_path)
    
    image_type = cover_image_file_name.split('.')[-1]
    #return StreamingResponse(io.BytesIO(cover_image.content), media_type=f"image/{image_type}")
    return Response(content=cover_image_content) 

@app.get('/books/thumbnail/{book_path:path}')
def get_book_cover_thumbnail(book_path):
    file_path = get_book_file_path(book_path)
    cover_image_content, cover_image_file_name = get_cover(file_path)

    pimg = Image.open(io.BytesIO(cover_image_content))
    pimg.thumbnail((100,100))
    with io.BytesIO() as output:
        pimg.save(output, format='png')
        pcontents = output.getvalue()
        gc.collect()
    return Response(content=pcontents, media_type='image/png')#, header={'Content-Length': len(pcontents)})
 
@app.get("/file/{path}")
def get_file(path):
    some_file_path = f'/data/{path}'
    return FileResponse(some_file_path)

@app.get('/books/file/{book_path:path}')
async def get_book_file(book_path):
    file_path = get_book_file_path(book_path)
    return FileResponse(file_path)

@app.get('/gc')
def do_gc():
    gc.collect()

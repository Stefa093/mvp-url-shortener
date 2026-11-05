import secrets
import string

from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, AnyHttpUrl, TypeAdapter, ValidationError

app = FastAPI()

ALPHABET = string.ascii_letters + string.digits # Alfabeto que se utilizará para generar la URL corta

existing_short_urls = {}  # Diccionario que contiene las URLs cortas existentes

validator = TypeAdapter(AnyHttpUrl) # Se crea un adaptador de tipo AnyHttpUrl de Pydantic para validar la URL

class ShortenRequest(BaseModel):
    url: str
    label: str | None = None # puede no contener valor, por lo que se define como opcional

def validate_url(url: str) -> str: # Función para validar la URL utilizando el adaptador de tipo AnyHttpUrl de Pydantic    
    try: 
        answer = validator.validate_python(url)
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL"
        ) from None # evitamos que se muestre una cadena de excepciones que no aporta informacion útil en este caso
    return str(answer)

def generate_short_url(length: int = 6) -> str: # Función para generar una URL corta aleatoria
    while True:
        short_url = ''.join(
            secrets.choice(ALPHABET) 
            for _ in range(length)
        )
        # Aquí se debería verificar si la URL corta ya existe en la base de datos
        # Si no existe, se retorna la URL corta generada
        if short_url not in existing_short_urls:  
            return short_url

@app.get("/")
def start():
    return {"message": "URL Shortener running"}

@app.post("/shorten", status_code=201)
def shorten_url(data: ShortenRequest, request: Request):
    # Validación de la URL
    validated_url = validate_url(data.url) # Validamos antes de acortar la URL, si no es válida se lanza una excepción HTTP con código 400 y un mensaje de error
    # Lógica para acortar la URL
    codee = generate_short_url()
    
    existing_short_urls[codee] = { # Se guarda la URL original y la etiqueta en el diccionario de URLs cortas existentes 
        "url": validated_url, 
        "label": data.label,
        "created_at": datetime.now(timezone.utc).isoformat(), # Se obtiene la fecha y hora actual en formato ISO 8601
        "clicks": []  # Se inicializa una lista vacía para almacenar los clicks en la URL corta
    }

    short_url = str(request.base_url).rstrip("/") +  "/" + codee # Se construye la URL corta completa utilizando la URL base del request y el código generado

    return {
        "code": codee,
        "short_url": short_url
    }

# se agrega un endpoint para obtener las estadísticas de la URL corta utilizando el código de la URL corta
# primero se define la ruta del endpoint y el método HTTP que se utilizará (GET)

@app.get("/stats/{code}") # Endpoint para obtener las estadísticas de la URL corta utilizando el código de la URL corta
def get_stats(code: str):
    existing_url = existing_short_urls.get(code)
    # Lógica para obtener las estadísticas de la URL corta
    if existing_url is None: # comprobación de si la URL corta existe en el diccionario de URLs cortas existentes
        raise HTTPException(
            status_code=404, 
            detail="Short URL not found"
        )
    clicks = existing_url["clicks"]

    last_click = (
        clicks[-1]["timestamp"] 
        if clicks 
        else None
    )
    return {
        "code": code,
        "original_url": existing_url["url"],
        "label": existing_url["label"],
        "created_at": existing_url["created_at"],
        "total_clicks": len(clicks), # Se obtiene el número de clicks en la URL corta
        "last_click": last_click
    } # type: ignore


@app.get("/{code}") # Endpoint para redirigir a la URL original utilizando el código de la URL corta
def redirect_to_url(code: str, request: Request):
    existing_url = existing_short_urls.get(code)
    # Lógica para redirigir a la URL original
    if existing_url is None: # comprobación de si la URL corta existe en el diccionario de URLs cortas existentes
        raise HTTPException(
            status_code=404, 
            detail="Short URL not found"
    )
    existing_url["clicks"].append({ # Se agrega un registro de click en la URL corta
        "timestamp": datetime.now(timezone.utc).isoformat(), 
        "user_agent": request.headers.get("user-agent") 
    })

    return RedirectResponse( 
        url=existing_url["url"],
        status_code=302
    )

# Soporte para este metodo de modo que se pueda comprobar sin alterar el contador de clics de manera artificial.
@app.head("/{code}") # Endpoint para redirigir a la URL original utilizando el código de la URL corta, pero sin devolver el contenido de la página
def head_redirect_to_url(code: str):
    existing_url = existing_short_urls.get(code)
    # Lógica para redirigir a la URL original
    if existing_url is None: # comprobación de si la URL corta existe en el diccionario de URLs cortas existentes
        raise HTTPException(
            status_code=404, 
            detail="Short URL not found"
        )
    return RedirectResponse( 
        url=existing_url["url"],
        status_code=302
    )
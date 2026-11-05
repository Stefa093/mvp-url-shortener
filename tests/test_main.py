from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Prueba para crear una URL corta
def test_create_short_url(): 
    response = client.post("/shorten", json={"url": "https://www.example.com", "label": "Test"})
    assert response.status_code == 201
    data = response.json()
    assert "code" in data
    assert "short_url" in data
    assert len(data["code"]) == 6  # Verifica que el código generado tenga una longitud de 6 caracteres

# Prueba para la redirección a la URL original utilizando el código de la URL corta
def test_redirect_to_url():
    # Primero, creamos una URL corta para obtener un código válido
    created = client.post("/shorten", json={"url": "https://example.com", "label": "Redirect Test"})
    code = created.json()["code"]

    # Ahora, probamos la redirección utilizando el código obtenido
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302  # Verifica que la respuesta sea una redirección
    assert response.headers["location"] == "https://example.com/"  # Verifica que la URL de redirección sea la correcta

# Prueba para obtener el conteo de clicks en la URL corta
def test_click_count():
    # Primero, creamos una URL corta para obtener un código válido
    created = client.post("/shorten", json={"url": "https://www.example.com", "label": "Click Count Test"})
    code = created.json()["code"]

    # Simulamos algunos clicks en la URL corta
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)

    # Ahora, probamos el endpoint de estadísticas para obtener el conteo de clicks
    response = client.get(f"/stats/{code}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_clicks"] == 3  # Verifica que el conteo de clicks sea correcto

# Prueba de URL corta inválida
def test_invalid_short_url():
    response = client.post("/shorten", json={"url": "ftp://example.com"})
    assert response.status_code == 400

# Prueba de código de URL corta desconocido
def test_unknown_short_url_code():
    response = client.get("/stats/unknowncode")
    assert response.status_code == 404
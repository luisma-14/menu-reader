from fastapi import FastAPI
from pydantic import BaseModel
import requests
from PIL import Image
from io import BytesIO
import pdfplumber
import pytesseract
from bs4 import BeautifulSoup

app = FastAPI()

class MenuRequest(BaseModel):
    menu_url: str

def extract_text_from_pdf(content):
    text = ""
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(content):
    image = Image.open(BytesIO(content))
    return pytesseract.image_to_string(image)

def extract_text_from_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(separator="\n")

@app.post("/extraer-menu")
def extraer_menu(request: MenuRequest):
    url = request.menu_url
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "")

    if "pdf" in content_type:
        text = extract_text_from_pdf(response.content)
    elif "image" in content_type:
        text = extract_text_from_image(response.content)
    elif "html" in content_type or url.endswith(".html"):
        text = extract_text_from_html(response.content)
    else:
        return {"error": "Tipo de contenido no compatible"}

    return {
        "url": url,
        "menu_text": text.strip()
    }

from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from bs4 import BeautifulSoup
import pandas as pd
import requests
import uuid

app = FastAPI()

def fetch_sitemap_urls(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        return [loc.get_text() for loc in soup.find_all('loc')]
    except Exception as e:
        return []

def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code
    except Exception as e:
        return f"Error: {e}"

@app.get("/", response_class=HTMLResponse)
async def form():
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sitemap URL Checker</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 50px; text-align: center; }
                form { background: white; padding: 30px; border-radius: 8px; display: inline-block; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                input[type=text] { width: 80%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
                button { padding: 10px 20px; background-color: #28a745; border: none; color: white; border-radius: 4px; cursor: pointer; }
                button:hover { background-color: #218838; }
            </style>
        </head>
        <body>
            <form action="/check" method="post">
                <h2>Check Sitemap URL Status</h2>
                <input type="text" name="sitemap_url" placeholder="Enter sitemap URL" required>
                <br>
                <button type="submit">Check URLs</button>
            </form>
        </body>
        </html>
    """

@app.post("/check")
async def check(sitemap_url: str = Form(...)):
    urls = fetch_sitemap_urls(sitemap_url)

    if not urls:
        return {"error": "No URLs found or invalid sitemap."}

    data = [{"URL": url, "Status": check_url_status(url)} for url in urls]
    df = pd.DataFrame(data)

    filename = f"/tmp/sitemap_status_{uuid.uuid4().hex}.xlsx"
    df.to_excel(filename, index=False)

    return FileResponse(
        filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename="sitemap_status.xlsx"
    )


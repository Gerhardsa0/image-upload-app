from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import shutil
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict

app = FastAPI(title="Image Number Submission API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ordner erstellen
UPLOAD_DIR = "uploads"
DATA_FILE = "submissions.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Templates und statische Dateien
templates = Jinja2Templates(directory="templates")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")


def load_submissions() -> List[Dict]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_submissions(submissions: List[Dict]):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, indent=2, ensure_ascii=False, default=str)


# Web Interface Route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    submissions = load_submissions()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "submissions": submissions
    })


# Deine bestehenden API Routes...
@app.post("/api/submit")
async def submit_data(
        image: UploadFile = File(...),
        number: float = Form(...),
        user_name: str = Form(...)
):
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if image.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported image format: {image.content_type}")

    try:
        file_extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        submissions = load_submissions()

        new_submission = {
            "id": len(submissions) + 1,
            "user_name": user_name,
            "number": number,
            "image_filename": unique_filename,
            "image_url": f"/uploads/{unique_filename}",
            "created_at": datetime.now().isoformat()
        }

        submissions.append(new_submission)
        save_submissions(submissions)

        print(f"✅ New submission: {user_name} - {number} - Image: {unique_filename}")

        return {
            "message": "Submission successful",
            "id": new_submission["id"],
            "image_url": new_submission["image_url"]
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/submissions")
async def get_submissions():
    submissions = load_submissions()
    return {
        "total": len(submissions),
        "submissions": submissions
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting server...")
    print("🌐 Web Interface: http://localhost:8000")
    print("👨‍💼 Admin Panel: http://localhost:8000/admin")
    print("📖 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
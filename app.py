from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import shutil
import os
import uuid

from parser import TemplateParser
from replacer import CVReplacer
from exporter import CVExporter

app = FastAPI(
    title="CV Layout Preserver API",
    version="1.0.0"
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "CV Layout Preserver API",
        "status": "running"
    }


@app.post("/generate")
async def generate_cv(
    template: UploadFile = File(...),
    profile: UploadFile = File(...)
):
    try:
        template_path = os.path.join(
            UPLOAD_DIR,
            f"{uuid.uuid4()}_{template.filename}"
        )

        profile_path = os.path.join(
            UPLOAD_DIR,
            f"{uuid.uuid4()}_{profile.filename}"
        )

        with open(template_path, "wb") as f:
            shutil.copyfileobj(template.file, f)

        with open(profile_path, "wb") as f:
            shutil.copyfileobj(profile.file, f)

        parser = TemplateParser(template_path)
        layout = parser.extract_layout()

        replacer = CVReplacer(
            layout=layout,
            profile_file=profile_path
        )

        document = replacer.generate()

        output_file = os.path.join(
            OUTPUT_DIR,
            f"{uuid.uuid4()}.pdf"
        )

        exporter = CVExporter(document)
        exporter.export_pdf(output_file)

        return FileResponse(
            output_file,
            filename="generated_cv.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

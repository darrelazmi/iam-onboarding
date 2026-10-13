from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import subprocess
import tempfile
import os

app = FastAPI()

def cleanup_files(md_path, pdf_path):
    if os.path.exists(md_path): os.remove(md_path)
    if os.path.exists(pdf_path): os.remove(pdf_path)

@app.post("/convert")
async def convert_markdown_to_pdf(markdown_content: str = Body(..., media_type="text/plain")):
    if not markdown_content.strip():
        raise HTTPException(status_code=400, detail="Markdown content cannot be empty.")

    # Create temporary files for the Markdown input and PDF output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)
        md_path = md_file.name

    pdf_path = md_path.replace(".md", ".pdf")

    try:
        # Run Pandoc using weasyprint engine
        cmd = [
            "pandoc",
            md_path,
            "-o", pdf_path,
            "--pdf-engine=weasyprint",
            "--css=style.css"
        ]

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Return the generated PDF and trigger background cleanup
        return FileResponse(
            path=pdf_path,
            filename="incident_report.pdf",
            media_type="application/pdf",
            background=BackgroundTask(cleanup_files, md_path, pdf_path)
        )

    except subprocess.CalledProcessError as e:
        cleanup_files(md_path, pdf_path)
        raise HTTPException(status_code=500, detail=f"Pandoc execution failed: {e.stderr}")

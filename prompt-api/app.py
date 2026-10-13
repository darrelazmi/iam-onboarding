import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from google import genai
from prompts import SOC_REPORT_PROMPT

app = FastAPI(title="MD Incident Report Generator")

# Initialize Gemini Client (Ensure GEMINI_API_KEY environment variable is set)
client = genai.Client()

def cleanup_file(path: str):
    """Deletes the temporary markdown file after it is sent to the user."""
    if os.path.exists(path):
        os.remove(path)

@app.post("/generate")
async def generate_report(file: UploadFile = File(...)):
    # Read the STIX file content
    try:
        stix_content = await file.read()
        stix_text = stix_content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Create a temporary path for the Markdown output
    md_path = tempfile.mktemp(suffix=".md")

    try:
        # Combine the imported instructions with the extracted STIX data
        full_prompt = f"{SOC_REPORT_PROMPT}\n\nCASE EVIDENCE:\n{stix_text}"

        # Call Gemini as the temporary LLM
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=full_prompt
        )

        # Write the LLM's Markdown response to disk
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(response.text)

        # Return the Markdown file and schedule cleanup
        return FileResponse(
            path=md_path,
            filename="incident_report.md",
            media_type="text/markdown",
            background=BackgroundTask(cleanup_file, md_path)
        )

    except Exception as e:
        cleanup_file(md_path)
        raise HTTPException(status_code=500, detail=str(e))

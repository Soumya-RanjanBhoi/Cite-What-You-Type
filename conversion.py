import subprocess
import os
from pathlib import Path
import shutil

async def convert_to_pdf(file_path: str, output_dir: str) -> Path:
    try:

        if shutil.which("soffice"):
            command="soffice"  # docker deployement ka samay
        else:
            command = r"C:\Program Files\LibreOffice\program\soffice.exe" #abhi ka liya
        
        subprocess.run([
            command,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            file_path
        ], check=True, capture_output=True)

        original_stem = Path(file_path).stem
        pdf_path = Path(output_dir) / f"{original_stem}.pdf"
        
        if pdf_path.exists():
            return pdf_path
        else:
            raise FileNotFoundError("Conversion finished but PDF not found.")
    
    except Exception as e:
        print(f"Conversion Error: {e}")
        raise
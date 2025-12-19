import subprocess
import os
from pathlib import Path

def convert_to_pdf(file_path: str, output_dir: str) -> Path:
    try:
        SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
        
        subprocess.run([
            SOFFICE_PATH,
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
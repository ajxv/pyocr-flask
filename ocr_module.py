# ocr_module.py
import pytesseract
from pdf2image import convert_from_path
import json
from pathlib import Path
import tempfile
import logging
from PIL import Image
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OCRResult:
    filename: str
    total_lines: int
    lines: List[str]
    success: bool
    error: Optional[str] = None


class OCRPDFExtractor:
    def __init__(self, tesseract_path: str = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        return image.convert('L').point(lambda x: 0 if x < 128 else 255, '1')

    def extract_lines(self, pdf_file) -> OCRResult:
        try:
            all_lines = []
            with tempfile.TemporaryDirectory() as temp_dir:
                # Handle both file path strings and file objects
                if isinstance(pdf_file, str):
                    images = convert_from_path(pdf_file)
                    filename = Path(pdf_file).name
                else:
                    # Save uploaded file temporarily
                    temp_path = Path(temp_dir) / "temp.pdf"
                    pdf_file.save(temp_path)
                    images = convert_from_path(str(temp_path))
                    filename = pdf_file.filename

                for i, image in enumerate(images, 1):
                    self.logger.info(f"Processing page {i}")
                    processed_image = self.preprocess_image(image)
                    text = pytesseract.image_to_string(
                        processed_image, lang='eng')
                    lines = text.split('\n')

                    if len(images) > 1:
                        lines = [f"[Page {i}] {line}" for line in lines]
                    all_lines.extend(lines)

            cleaned_lines = [line.strip()
                             for line in all_lines if line.strip()]
            return OCRResult(
                filename=filename,
                total_lines=len(cleaned_lines),
                lines=cleaned_lines,
                success=True
            )

        except Exception as e:
            self.logger.error(f"Error in OCR processing: {e}")
            return OCRResult(
                filename=getattr(pdf_file, 'filename', 'unknown'),
                total_lines=0,
                lines=[],
                success=False,
                error=str(e)
            )

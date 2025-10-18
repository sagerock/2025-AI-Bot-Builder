from typing import Optional, List
import io
import logging
from pathlib import Path
from pypdf import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR processing of scanned documents"""

    # Threshold for determining if a PDF needs OCR (words per page)
    TEXT_THRESHOLD_PER_PAGE = 50

    @staticmethod
    def _detect_if_scanned(file_content: bytes) -> bool:
        """
        Detect if a PDF is scanned (image-based) by checking text content

        Args:
            file_content: Binary content of the PDF file

        Returns:
            True if the PDF appears to be scanned (needs OCR), False otherwise
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)

            total_words = 0
            pages_checked = min(3, len(pdf_reader.pages))  # Check first 3 pages

            for page in pdf_reader.pages[:pages_checked]:
                text = page.extract_text()
                words = len(text.split())
                total_words += words

            avg_words_per_page = total_words / pages_checked if pages_checked > 0 else 0

            # If average words per page is below threshold, assume it's scanned
            is_scanned = avg_words_per_page < OCRService.TEXT_THRESHOLD_PER_PAGE

            logger.info(f"PDF analysis: {avg_words_per_page:.0f} words/page average. Scanned: {is_scanned}")
            return is_scanned

        except Exception as e:
            logger.warning(f"Error detecting if PDF is scanned: {e}. Assuming it needs OCR.")
            return True

    @staticmethod
    def _ocr_image(image: Image.Image) -> str:
        """
        Perform OCR on a single image

        Args:
            image: PIL Image object

        Returns:
            Extracted text from the image
        """
        try:
            # Use pytesseract with optimized settings for textbooks
            custom_config = r'--oem 3 --psm 1'  # OEM 3 = Default, PSM 1 = Auto page segmentation with OSD
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"OCR failed for image: {e}")
            return ""

    @staticmethod
    def ocr_pdf(file_content: bytes, dpi: int = 300) -> str:
        """
        Perform OCR on a PDF file

        Args:
            file_content: Binary content of the PDF file
            dpi: DPI for image conversion (higher = better quality but slower)

        Returns:
            Extracted text from all pages
        """
        try:
            logger.info(f"Starting OCR processing with DPI={dpi}")

            # Convert PDF pages to images
            images = convert_from_bytes(
                file_content,
                dpi=dpi,
                fmt='jpeg',
                thread_count=4  # Use multiple threads for faster processing
            )

            logger.info(f"Converted PDF to {len(images)} images")

            # OCR each page
            text_parts = []
            for page_num, image in enumerate(images, 1):
                logger.info(f"OCR processing page {page_num}/{len(images)}")
                page_text = OCRService._ocr_image(image)

                if page_text.strip():
                    text_parts.append(f"[Page {page_num}]\n{page_text}")

            full_text = "\n\n".join(text_parts)
            logger.info(f"OCR completed. Extracted {len(full_text)} characters from {len(images)} pages")

            return full_text

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise ValueError(f"Failed to perform OCR on PDF: {str(e)}")

    @staticmethod
    def extract_text_from_pdf_with_ocr(file_content: bytes, force_ocr: bool = False) -> str:
        """
        Extract text from PDF, using OCR if necessary

        Args:
            file_content: Binary content of the PDF file
            force_ocr: If True, always use OCR regardless of text detection

        Returns:
            Extracted text content
        """
        try:
            # Check if PDF needs OCR
            needs_ocr = force_ocr or OCRService._detect_if_scanned(file_content)

            if needs_ocr:
                logger.info("PDF appears to be scanned. Using OCR extraction.")
                return OCRService.ocr_pdf(file_content)
            else:
                logger.info("PDF has embedded text. Using standard extraction.")
                # Use standard pypdf extraction
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PdfReader(pdf_file)

                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"[Page {page_num}]\n{text}")

                return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")


# Singleton instance
ocr_service = OCRService()

"""
login.py

Helper for logging into the site, solving the CAPTCHA via OCR (Tesseract).

Design notes:
- Tesseract configuration is split out so it can be tested and reused.
- CAPTCHA OCR is inherently flaky; this module retries a bounded number of times.
- All public functions are type-annotated.

Dependencies:
- pillow (PIL)
- pytesseract (wrapper)
- system tesseract binary available on PATH (or provided explicitly)
- selenium
"""

from .login import login

__all__ = [
    'login'
]
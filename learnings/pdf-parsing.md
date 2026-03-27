# PDF Parsing

- **Image-based PDFs** (scanned documents) require OCR, not just text extraction. `pdftotext` and PyMuPDF (`fitz`) only extract embedded text. For scanned PDFs, use `tesseract` or `poppler` with OCR flags.

from docling.document_converter import DocumentConverter

# Docling automatically uses GPU when available
converter = DocumentConverter()
result = converter.convert("/home/rahul/Desktop/CHUNK-MY-PDF/docs/pdfs/table.pdf")

# Store the result in a .md file
with open("/home/rahul/Desktop/CHUNK-MY-PDF/docs/markdown/table.md", "w") as f:
    f.write(result.document.export_to_markdown())
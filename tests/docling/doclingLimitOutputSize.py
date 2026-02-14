from pathlib import Path
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source, max_num_pages=100, max_file_size=20971520)

with open("/home/rahul/Desktop/CHUNK-MY-PDF/docs/markdown/arxiv_2408.09869.md", "w") as f:
    f.write(result.document.export_to_markdown())
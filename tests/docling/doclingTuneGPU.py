from docling.document_converter import DocumentConverter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions

# Explicitly configure GPU acceleration
accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.CUDA,  # Use CUDA for NVIDIA GPUs
)

# Configure pipeline for optimal GPU performance
pipeline_options = ThreadedPdfPipelineOptions(
    ocr_batch_size=64,      # Increase batch size for GPU
    layout_batch_size=64,   # Increase batch size for GPU
    table_batch_size=4,
)

# Create converter with custom settings
converter = DocumentConverter(
    accelerator_options=accelerator_options,
    pipeline_options=pipeline_options,
)

# Convert documents
result = converter.convert("docs/pdfs/table.pdf")
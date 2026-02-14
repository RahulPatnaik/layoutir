
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmConvertOptions,
    VlmPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

# Convert a public arXiv PDF; replace with a local path if preferred.
source = "https://arxiv.org/pdf/2501.17887"

###### EXAMPLE 2: USING PRESETS (RECOMMENDED)
# - Uses the "granite_docling" preset explicitly
# - Same as default but more explicit and configurable
# - Auto-selects the best runtime for your platform (Transformers by default)

vlm_options = VlmConvertOptions.from_preset("granite_docling")

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=VlmPipelineOptions(vlm_options=vlm_options),
        ),
    }
)

doc = converter.convert(source=source).document

with open("/home/rahul/Desktop/CHUNK-MY-PDF/docs/markdown/table_vlm.md", "w") as f:
    f.write(doc.export_to_markdown())


## Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion

Nikolaos Lavinathinos ", Christoph Auer ", Miksym Lysak, Ahmed Nassar, Michele Dolfi, Panagiotis Vagenas, Cesar Berrospi, Matteo Omenetti, Kasper Dinkla, Yusik Kim, Shubham Gupta, Rafael Teixeira de Lima, Valery Weber, Lucas Morin, Ingmar Meijer, Viktor Kuropiatnyk, Peter W. J. Staar

IBM Research, Rüschlikon, Switzerland

Please send correspondence to: deepsearch-core@zurich.ibm.com

Abstract

We introduce Docling , a easy-to-use, self-contained, MIT licensed, open-source toolkit for document conversion, that can parse several types of document formats into a unified, richly structured representation. It is powered by state-of-the-art specializé AI models for layout analysis (DocLayNet) and table structure recognition (tableFormer), and is efficiently on-commodity hardware in a small resear e budget. Docling is released as a Python package and can be used as a Python API or as a CLI tool. Docling's modular design allows it to be integrated with other architecture and efficient document representation make it easy to implement extensions, new features, models, and customizations. It has been already integrated in other open-source frameworks (e.g., LangChain, LlamaDex, spaCy), making it a natural fit for the processing of documents.

In this paper, we present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

and develop a new tool for document conversion

We present a novel approach to Docling

With Docling , we recently explore a very capable and efficient document conversion tool which builds on the powerful, specialized AI models for layout analysis and table structure recognition that we developed and presented in the recent past (Lavinathinos et al. 2021; Pitzmann et al. 2022; Lysak et al. 2023; Docling is designed as a simple, self-contained Python library with permissive MIT license, running entirely locally on commodity hardware. Its code architecture allows for easy extensibility and addition of new features and models. Since its launch in July 2024, Docling has attracted considerable attention in the AI community and ranks up on GitHub.

Figure 1: Sketch of 1Docling's pipelines and usage model. Both PDF pipeline and simpli e pipeline build up a DoclingDocument representation, which can be further enriched by Docling's API to inspect, export, or chunk the document for various purposes.

<!-- image -->

to hallucinations, conversion quality, time-to-solution, and compute resource requirements.

The most popular conversion tools today leverage vision language models (VLMs), which process page images to text and markup directly. Among proprietary solutions, GPT-4o (OpenAI), Claude (Anthropic), and Geminni (Google). In the open-source do-mains, LVA-based models, such as LLaVA-next, are note-worthy. However, all generative AI-based models face significant challenges. First, they are prone to hallucinations, which are the output of false information. In i.e., their output can contain false information which is not present in the source document.

When faithful transcription of document content is required, Second, these models demand substantial computational re-sources, making the conversion process expensive. Consequently, VLMs-based tools are typically offered as SaaS.

with compute-intensive operations performed remotely in the cloud. A second category of solutions prioritizes on-premises deployment, either as Web APIs or as libraries. Examples include Adobe Acrobat, Grobid, Marker, Miner Unstruc tured, and others. These solutions often rely on multiple specialized models, such as OCR, layout analysis, and table recognition models. Docling

ing modular, task-specifi c models which recover document structure and features only. All text content is taken from the programmatic PDF or transcribed through OCR methods. This design ensures faithful conversion, without the risk of generating false content. However, it necessitates that training a diverse set of models for different document com-

ponents, such as formulas or figures. Within this category, Iocdling distinguishes itself through its permissive MIT license, allowing organizations to integrate Docling into their solutions without incurring fees or adopting restrictive licenses (e.g., GPL).

## 3 Design and Architecture

Docling is designed in a modular fashion with extensibil ity in mind, and it builds on three main concepts: pipelines, parser backends, and the DoclingDocument data model.

## 3 Design and Architecture

Docling is designed in a modular fashion with extensibil ity in mind, and it builds on three main concepts: pipelines, parser backends, and the DoclingDocument data model. As its centerpiece, Docling (Figure 1) provides a backends that can be used to construct pipelines and parser backends. Docling provides a rich set of capabilities for constructing pipelines and parser backends, including the ability to construct pipelines and parser backends from a single document, and the ability to construct pipelines and parser backends from a single document.

## 3 Design and Architecture

Docling is designed in a modular fashion with extensibil ity in mind, and it builds on three main concepts: pipelines, parser backends, and the DoclingDocument data model.

## 3 Design and Architecture

Docling is designed in a modular fashion with extensibil ity in mind, and it builds on three main concepts: pipelines, parser backends, and the DoclingDocument data model.

- · Docling is designed in a modular fashion with extensibil ity in mind, and it builds on three main concepts: pipelines, parser backends, and the DoclingDocument data model.
- · Docling is designed in a modular fashion with extensibil ity in mind, and it builds on three main concepts: pipelines, parser backends, and the DoclingDocument data model.

Docling enables representing doc-ument content in a unified manner, i.e., regardless of the source document format.

Besides specifying the data model, the docling class defines APIs encompassing document construction, inspection, and export. Using the respective methods, users can incrementally build a doclingDocument, traverse its contents in reading order, or export commonly used formats such as JSON and lossless serialization to (and deserialization from) JSON, and lossy export formats such as Markdown and HTML, which, unlike JSON, cannot retain all available meta information.

A doclingDocument can additionally be passed to a chunker class, an abstraction that returns a stream of chunks, each of which captures some part of the document as a string. accompanied by respective metadata. To enable both flexi-bility for downstream applications and out-of-the-box utili-ity, Docling defines a chunker class hierarchy, providing a base type as well as specific subclasses. By using the base type, downstream applications can leverage popular frameworks like LangChainer or LlamaIndex, which provide a high degree of flexibility in the chunking approach.

## 

## 4.1.2.3.3.4.5.6.7.8.9.10

Table 1: Versions and configuration options considered for each tested asset. * denotes the default setting.

|              | Asset   | Version                     | OCR            | Layout               | Tables   |
|--------------|---------|-----------------------------|----------------|----------------------|----------|
| Docling      | 2.5.2   | EasyOCR*                    | default        | TableFormer (fast) * | *        |
| Marker       | 0.3.10  | Surya                       | default        | default              | default  |
| MinerU       | 0.9.3   | auto *                      | doclayout_yolo | rapid_table *        | *        |
| Unstructured | 0.16.5  | hi_res with table structure |                |                      |          |

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

large range between 5 and 95 percentiles results from the highly different complexes across pages (i.e., most empty pages vs. full-page tables).

Disabling OCR saves 6% of runtime on the x86 CPU and the M3 Max SoC, and 50% on the L4 GPU. Turning off table structure recognition saves 16% of runtime on the x86 CPU and the M3 Max SoC, and 24% on the L4 GPU. Disabling both OCR and table structure recognition saves around 75% of runtime on all system configurations.

Profiling Dcling's AI Pipeline We analyzed the contributi ng of Docling's PDB backend and all AI models in the results are shown in Figure 4. On average, processing a page took 481 ms on the L4 GPU, 3.1 s on the x86 CPU and 1.26 s on the M3 Max SoC.

It is evident that applying OCR is the most expensive operation. In our benchmark dataset, OCR engages in 578 pages on the x86 CPU and 5 s on the M3 Max SoC. The layout model spent 44 ms on the L4 GPU, 633 ms on the x86 CPU and 271 ms on the M3 Max SoC. On average, for each page, it is the cheapest of the models, while Table 1 shows the performance of the AI model on the x86 GPU and 410 ms on the M3 Max SoC. While Table 1 shows the performance of the AI model on the x86 CPU and 74 ms on the M3 Max SoC, Table 1 shows the performance of the AI model on the x86 GPU and 1.26 s on the M3 Max SoC.

On the L4 GPU, we observe a speedup of 8 x (OCR), 14 x (Table 1) and 4 x (Table 2) and a speedup of 3 x (OCR), 6 x (Layout model) and 1.7 x (Table 3) compared to the M3 Max CPU. Our MacBook Pro. This shows that OCR is no equal benefit for all AI models from the GPU acceleration and there might be potential for optimization.

The time spent in parsing a PDF page through our docling-parse backend is substantially lower in comparison to the AI models. On average, parsing a PDF page took 81 ms on the x86 CPU and 444 ms on the M3 Max SoC (there is no GPU support).

Comparison to Other Tools We compare the average times to convert a page to between Docling, Marker Miner, and Unstructured on the system configurations outlined in section 5.2. Results are shown in Figure 5.

Without GPU support, Docling leads with 3.1 sec/page (x86 CPU) and 1.27 sec/page (M3 Max SoC), followed by Miner (3.3 sec/page on x86 CPU) and Unstructured (4.2 sec/page on x86 CPU) and 2.7 sec/page on M3 Max SoC), while Marker neece d over 16 sec/page (x86 CPU) and 4.2 sec/page (M3 Max SoC). Miner, despite several efforts to configure its environment, did not finish any run on our MacBook Pro M3 Max. With CUDA acceleration on the Nvidia L4 GPU, the picture changes and Miner takes over with 0.49 sec/page with Docling and 0.86 sec/page with Marker. Unstructured does not profit from GPU acceleration.

## 6 Applications

Docling's document extraction capabilities make it naturally suitable for workflows like generative AI applications (e.g., RAG), data preparation for foundation model training, and fine-tuning, as well as information extraction.

As far as RAG is concerned, users can leverage existing Docling extensions for popular frameworks like LlamaMin dex and then harness framework capabilities for RAG components like embedding models, vector stores, etc. These docling extensions typically provide two modes of operation: one using a lossy export, e.g., to Markdown, and one using lossless serialization via JSON. The former provides a simple starting point upon which any text-based chunk can be added to a framework. This method may be applied, e.g., to drawing from the framework library, while the latter, which uses a swappable Docling chunker, can be the more powerful one, as it can provide document-native RAG grounding via rich meta data such as the page number and the bounding box of the document. Supporting context, users can still usage Docling to accelerate and simplify the development of their custom pipelines. Besides strict RAG pipelines for Q&amp;A, Docling can naturally be utilized in the context of broader agerative workflows for which it can provide document-based knowledge for agents to de-cide and act on.

<!-- image -->

<!-- image -->

Figure 4: Contributions of PDF backend and AI models to the conversion time of a page (in seconds per page). Lower is better. Left: Ranges of time contributions for each model to pages it was applied on (i.e., OCR was applied only on pages with tables, and the benchmark dataset (factoring in zero-time contribution for OCR and table structure models on pages without bitmaps or tables) .

<!-- image -->

Figure 5: Conversion time in seconds per page on our dataset in three scenarios, across all assets and system configurations. Lower bars are bett e r. The configuration includes OCR and table structure recognition (fast table option on Doccling and MinerU, hi\_res in unstructured, as shown in tabl e 1).

<!-- image -->

where it supports the enhncement of the knowledge taxonomy.

Docling is also available and officially maintained as a system package in the Red Hat ® Enterprise Linux ® AI (RHEL AI) distribution, which seamlessly allows to de velop, test, and run the Granite family of large language models for enterprise applications.

by Docling, such as layout analysis, table structure recognition, and reading order detection, text transcription, etc. This will allow transparent quality comparisons based on publicly available benchmarks such as DP-Bench (Zhong 2020), OmdiDocbench (Ouyang et al. 2024), and

be published in a future update of this technical report. The codebase of Docling is ope n for use under the MIT

license agreement and its roadmap is outlined in the discussions section 1 of our GitHub repository. We encourage everyone to propose improvements and make contributions.

## References

1. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

2. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

3. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

4. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

5. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

6. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

7. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

8. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

9. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

10. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

11. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

12. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

13. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

14. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

15. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

16. "The GitHub repository is a good place to start". GitHub.com. Retrieved 2021-03-20.

17. "The GitHub repository is a good place to start". GitHub.com.

Ouyang, L.; Qu, Y.; Zhou, H.; Zhu, J.; Zhang, R.; Lin, Q.; Wang, B.; Zhao, Z.; Jiang, M.; Zhao, X.; Shi, J.; Wu, F.; Chu, P.; Liu, M.; Li, Z.; Xu, C.; Zhang, B.; Shi, B.; Tu, Z.; and He, C. 2024. OmniDocBench: Benchmarking Diverse PDF Document with Comprehensive Annotations. arXiv:2412.07624.

Paruchuri, V. 2024. Marker: Convert PDF to Markdown Quickly with High Accuracy. https://github.com/Vikichurati/marker.

Pfitzmann, B.; Auer, C.; Dolci, M.; Nassar, A. S.; and Staar, P. 2022. DocLayer: a large nano-annotated dataset for document-layout segmentation. 37:3-3751.

Papydai, M. 2022. Papydai: A Papydai-Python PDF library. https://github.com/2022-papydai.pdf.

PPyPDFium Team. 2022. PPyPDFium: Python bindings for PDFium. https://github.com/papydium-team/papydiumfi.

PPyDictionn Library: A Papydai-Python PDF library. https://github.com/papydium-team/papydiumfi.

Sudairaj, S.; Bhandwal, A.; Parreja, A.; Xu, K.; Cox, D. 2022. Srivastava, A. 2024. Lattice: Large-scale Alignment for ChatBots. arXiv:2403.01081.

Saritsar, M.; Stanislaw, K.; Kaczmarek, K.; Dyda, P.; and Graliński, F. 2023. Cspdf: Building a high Quality Corpus for Visually Rich Documents from Web Crawl. In Fink. G. A. Jain, R. K.; and Z. K. Zadibi, R. eds., Document Analysis and Recognition - ICDAR 2023. 348-365. Cham. Springer Nature, ISBN 978-3-031-41682-9.

Unstructured.io Team. 2022. Unstructured.io: Open-source. Source-Processing Tools. https://unstructured.io/xv.pdf. Accessed: 2024-04-19.

Wang, B.; Xu, C.; Zhao, X.; Ouyang, L.; Zhang, F.; Zhang, B.; Wei, L.; S.; Z.; Li, W.; Qi, Sh.; Xiao, Y.; Lin, D.; and He. An Open-Source for Precise Document Content Extraction. arXiv:2409.9389.

Wolf, T.; Delun, S.; Vahani, M.; Simek, M.; Moin, A.; Cistac, P.; von Rapt; L.; Wolf, R.; Furtowicz, M.; Davi, J.; Shleifer, S.; von Platen, Z.; and Xu, C.; Scao, T. L.; Gugger, S.; Drame, M.; Lhoest, Q.; and Rush, A. M. 2020. HuggingFace: A transformer-based model for the art-natural language processing. arXiv:1910.03701.

Wang, B.; Xu, C.; Zhao, X.; Ouyang, L.; Zhang, F.; Zhang, B.; Wei, L.; S.; Z.; Li, W.; Qi, Sh.; Xiao, Y.; Lin, D.; and He. An Open-Source for Precise Document Content Extraction. arXiv:2403.08099.

Zhong, X. 2020. Image-based table recognition: data, model, and evaluation. arXiv:1911.10683.
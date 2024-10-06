# LLM-gym


### Understanding Math Behind large Language Models 
- [Minimal Introduction to Large Language Models](https://poloclub.github.io/transformer-explainer/) : Understand the High Level Concepts of Transformers Visually!
- [Understanding LLM Inference](https://kipp.ly/transformer-inference-arithmetic/) : Understand operations behind Kv-Cache , Flops Counting!
- [Quantization Principal](https://www.maartengrootendorst.com/blog/quantization/) : Understand types of quantization and how they can reduce memory overhead required for inferencing and training!
- [Calculate GPU Memory Required for Serving LLMS](https://www.substratus.ai/blog/calculating-gpu-memory-for-llm) : Reasons that make up memory for a LLM model!
- [LLM Underhood](https://bbycroft.net/llm) : Under-the-hood mechanics of Transformers technique!

### RAG Papers/Implementations
- [Speculative RAG](https://research.google/blog/speculative-rag-enhancing-retrieval-augmented-generation-through-drafting/) : Use Generalist RAG to rank multiple Answer Drafts from Specialist RAG!
- [Corrective RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_crag/) : Lookahead , decide whether correct or not , then rewrite the query if not correct!
- [Hyde Query Rewritting](https://www.pondhouse-data.com/blog/advanced-rag-hypothetical-document-embeddings) : Generate a hypothetical Document from the Query and search against that in the vector space!
- [Late Chunking Blog](https://weaviate.io/blog/late-chunking): Late chunking the sweet spot between naive chunking retrieval and late interaction based retrieval!
- [Contextual Rag](https://www.anthropic.com/news/contextual-retrieval) : While Indexing Ask LLM to contextualize the chunk and then index it!

### Some Essential Deployment Tools
- [Converting to GGUF Tools](https://www.substratus.ai/blog/converting-hf-model-gguf-model) : Converting LLM to GGUF Format!

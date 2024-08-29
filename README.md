# LLM-gym


### Understanding Math Behind large Language Models 
- [Understanding LLM Inference](https://kipp.ly/transformer-inference-arithmetic/) : Understand operations behind Kv-Cache , Flops Counting
- [Quantization Principal](https://www.maartengrootendorst.com/blog/quantization/) : Understand types of quantization and how they can reduce memory overhead required for inferencing and training

### RAG Papers/Implementations
- [Speculative RAG](https://research.google/blog/speculative-rag-enhancing-retrieval-augmented-generation-through-drafting/) : Use Generalist RAG to rank multiple Answer Drafts from Specialist RAG
- [Corrective RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_crag/) : Lookahead , decide whether correct or not , then rewrite the query if not correct
- [Hyde Query Rewritting](https://www.pondhouse-data.com/blog/advanced-rag-hypothetical-document-embeddings) : Generate a hypothetical Document from the Query and search against that in the vector space

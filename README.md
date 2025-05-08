# LLM-gym


### Understanding Math Behind large Language Models 
- [Minimal Introduction to Large Language Models](https://poloclub.github.io/transformer-explainer/) : Understand the High Level Concepts of Transformers Visually.
- [Understanding LLM Inference](https://kipp.ly/transformer-inference-arithmetic/) : Understand operations behind Kv-Cache , Flops Counting!
- [Quantization Principal](https://www.maartengrootendorst.com/blog/quantization/) : Understand types of quantization and how they can reduce memory overhead required for inferencing and training!
- [Calculate GPU Memory Required for Serving LLMS](https://www.substratus.ai/blog/calculating-gpu-memory-for-llm) : Reasons that make up memory for a LLM model!
- [LLM Underhood](https://bbycroft.net/llm) : Under-the-hood mechanics of Transformers technique.
- [Ai Compute Evolution](https://www.laconic.fi/ai-compute/) : How compute necessaties evolved over decades.

### RAG Papers/Implementations
- [Speculative RAG](https://research.google/blog/speculative-rag-enhancing-retrieval-augmented-generation-through-drafting/) : Use Generalist RAG to rank multiple Answer Drafts from Specialist RAG!
- [Corrective RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_crag/) : Lookahead , decide whether correct or not , then rewrite the query if not correct!
- [Hyde Query Rewritting](https://www.pondhouse-data.com/blog/advanced-rag-hypothetical-document-embeddings) : Generate a hypothetical Document from the Query and search against that in the vector space!
- [Late Chunking Blog](https://weaviate.io/blog/late-chunking): Late chunking the sweet spot between naive chunking retrieval and late interaction based retrieval!
- [Contextual Rag](https://www.anthropic.com/news/contextual-retrieval) : While Indexing Ask LLM to contextualize the chunk and then index it!
- [Retrieval via Late Interaction Models](https://huggingface.co/blog/fsommers/document-similarity-colpali) : Colipali and How it used Bag of Words for Document Similarity
- [Query Routing](https://github.com/PrithivirajDamodaran/Route0x) : A Set-Fit Based approach for query routing.

### Some Essential Deployment Tools
- [Converting to GGUF Tools](https://www.substratus.ai/blog/converting-hf-model-gguf-model) : Converting LLM to GGUF Format.

### About Vector Databases and Search Algorithms
- [HNSW Algorithm](https://lukesalamone.github.io/posts/how-does-hnsw-work/) : It shows the intution behind how the HNSW algorithm works.

### AI Safety and Harms
- [Incident Database](https://incidentdatabase.ai/apps/discover/?is_incident_report=true): Incidents and Reports of AI Harms.

### Agents & Systems
- [Building Effective Agentic Flows](https://www.anthropic.com/research/building-effective-agents): Building effective agents
- [LLM Systems](https://www.evidentlyai.com/ml-system-design): ML & LLM Systems
- [AI Co-Scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/): AI Co-Scientist
- [Building Agentic Sysmtes](https://huyenchip.com/2025/01/07/agents.html): Chip's guide to building Agentic Systems
- [Agent Frameworks Comparision](https://www.galileo.ai/blog/mastering-agents-langgraph-vs-autogen-vs-crew): Comparision against different Agents

### Benchmarks
- [Benchmarks](https://www.evidentlyai.com/llm-evaluation-benchmarks-datasets): Evaluation Datasets

### Data Creation / Preparation 
- [Tabular Synthetic Data Generation](https://docs.sdv.dev/sdv) : Synthetic Data Generation

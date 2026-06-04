# Design Note: Talk to Government Data

## 1. Stack & Decisions
*   **LLM**: Gemini-3-Flash-Preview (via Google Generative AI API). Chosen for its high context window and strong reasoning capabilities in structured output generation.
*   **Data Layer**: Pandas. Ideal for the size of this dataset (~3MB) and provides a rich set of transformation functions that an LLM can easily target.
*   **UI Framework**: Gradio. Recommended for Colab integration, providing a quick way to build a functional web UI without frontend overhead.
*   **Execution Strategy**: I chose to have the model emit **structured JSON** containing a pandas query string. This is a safer middle ground compared to raw `exec()`. By constraining the output to specific columns and operations defined in the schema prompt, we reduce the risk of arbitrary code execution.

## 2. Correctness & Trust
To prevent hallucinations, the system:
*   **Schema Pinning**: The LLM is provided with the exact column names and a sample of the data values.
*   **Direct Execution**: Answers are derived ONLY from the result of the pandas query, not the model's memory.
*   **Audit Trail**: The exact code that ran is surfaced to the user. A skeptical officer can verify the logic against the raw CSV.

## 3. Government Deployment
*   **Data Residency**: In a production environment, the data should stay within a VPC (e.g., Google Cloud Vertex AI) rather than being sent to a public API.
*   **Audit Trails**: Every question and the resulting query should be logged in a centralized database for compliance.
*   **Security**: Executing generated code is a risk. For production, I would use a **DSL (Domain Specific Language)** or a **Query Builder** interface that the LLM interacts with, rather than raw Pandas/SQL.

## 4. Scaling
When moving to hundreds of tables:
*   **Metadata Indexing**: We would need a semantic search (RAG) layer just to find the *right table* before asking the question.
*   **Query Optimization**: Standard Pandas would fail; we'd shift to **DuckDB** or **BigQuery** for large-scale analytical queries.
*   **Joins**: The LLM would need a sophisticated multi-step planning agent to handle complex joins across tables.

## 5. Validation
*   **User Testing**: I would test with non-technical staff by giving them a "sandbox" and asking them to verify if the NL answer matches their intuition of the data.
*   **Failure Modes**: I'd watch for "State Name Mismatches" (e.g., user asks for 'UP' but data has 'Uttar Pradesh') and handle them via fuzzy matching.

## 6. Honest Limitations
Currently, the prototype:
*   Uses a simple `eval()` which is not secure for public-facing production apps.
*   Doesn't handle complex time-series forecasting (it only does historical lookups).
*   Relies on the CSV structure being consistent; any change in the source URL's column naming would break the cleaner.

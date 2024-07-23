# Instructions to Run

## Prerequisites

1. **Python**: Ensure you have Python 3.10 or higher installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).

2. **Pip**: Ensure you have `pip` installed. It usually comes with Python. You can verify by running `pip --version` in your terminal.

## Setup

1. **Clone the Repository**:
   Download the project files from the repository or clone it using:
   ```bash
   git clone https://github.com/shandilyabh/silo.small
   cd silo.small
   ```
2. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Get Gemini API**:
  - go to: https://console.cloud.google.com/home/dashboard and sign in
  - click on `select project`: adjacent to the google cloud branding beside the search bar
  - click on `new project`: on the left of the pop up screen
  - enter details and press `Create project`
  - go to: https://aistudio.google.com/app/apikey
  - click on `create API Key`
  - select project
  - copy API Key

4. **Set up .env file**:
   In the terminal with silo.small as current directory:
   ```bash
   touch .env
   ```
   open .env file and paste the gemini api key under the variable name: `GEMINI_API_KEY`

4. **Run Silo**:
   ```bash
   python main.py /path/to/pdf
   ```
   > you can add a file's path by just dragging it into the terminal
   
   *test run*: Since, `Corpus.pdf` comes with the repository
   ```bash
   python main.py Corpus.pdf
   ```

#### Notes
- on the first run, Sentence Transformers will fetch Supabase's `gte-small` model for generating word embeddings.
- the first response from silo might have very high latency (~20s), but ones after will generated around 1-2 seconds.

### Architectural Decisions:
**silo uses**:
  - `Unstructured` Library for parsing the PDF and extracting text from it.
  - Langchain's `RecursiveCharachterTextSplitter()` for recursive chunking of text extracted.
  - Hugging Face's `Sentence Transformer` library for generating embeddings (model: supabase/gte-small)
    > 384-dimensional embeddings
  - `Faiss-cpu` for indexing the embeddings and search/retrieval of text_chunks.
    > IndexFlatL2
  - Google's `Gemini 1.5 Flash` for text-generation
  - silo is context aware. each session has a conversation history in order to preserve context (memory).
    > conversations are stored as JSON objects in `session_history.json`, serially, marked with UUIDs [uuid4() is used]
      - session object:
        ```
        session = {
              "id" : f"{uuid}",
              "conversation" : {
                    "user" : [""],
                    "silo" : [""]
              }
        }
        ```

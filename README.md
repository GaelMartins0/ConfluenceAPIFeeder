# ConfluenceAPIFeeder

ConfluenceAPIFeeder is a tool that leverages the Confluence API to feed data into an OpenAI Assistant or a Retrieval-Augmented Generation (RAG) model for the same assistant.

## Setup

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/GaelMartins0/ConfluenceAPIFeeder.git
    cd ConfluenceAPIFeeder
    ```

2. **Configure Environment Variables:**

    Fill the `.env` file in the root directory with your Confluence parameters along with the OpenAI API key. 

    ```plaintext
    OPENAI_API_KEY=your_api_key
    CONFLUENCE_URL=https://wiki.amplexor.com/confluence
    SPACE_KEY=space_key
    USERNAME=your_username
    API_TOKEN=your_api_token
    OUTPUT_DIR=Docs
    ```

## Usage

### 1. Export Files from Confluence API

Export all pages from a specified Confluence space:

```bash
python Confluence_export_all_pages.py
```

### 2. Export Files to OpenAI Vector Store

Export files with OpenAI Vector Store and access them with an assistant:

```bash
python Confluence_export_file_to_VS.py
```



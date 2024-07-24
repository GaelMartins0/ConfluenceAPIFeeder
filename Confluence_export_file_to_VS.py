# Command to run the script :
# python Confluence_export_file_to_VS.py --api_key YOUR_OPENAI_API_KEY   

import argparse
import os
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Export files to VS using the Confluence API.")
parser.add_argument('--api_key', required=True, help='Your OpenAI API key')
args = parser.parse_args()

# Initialize OpenAI client with the API key from command-line argument
client = OpenAI(api_key=args.api_key)

# Define the name for the vector store
vector_store_name = "Document Vector Store"

# List all vector stores to check if one with the same name already exists
existing_vector_stores = client.beta.vector_stores.list()
vector_store_id = None

for vs in existing_vector_stores.data:
    if vs.name == vector_store_name:
        vector_store_id = vs.id
        break

# If a vector store with the same name exists, delete it
if vector_store_id:
    print(f"Vector store with name '{vector_store_name}' already exists. Deleting it...")
    client.beta.vector_stores.delete(vector_store_id)
    print(f"Deleted vector store with ID {vector_store_id}")

# Create a new vector store
vector_store = client.beta.vector_stores.create(name=vector_store_name)

# Get list of PDF files in Docs directory
file_paths = [os.path.join("Docs", file) for file in os.listdir("Docs") if file.endswith(".pdf")]
file_streams = [open(path, "rb") for path in file_paths]

# Upload and poll the files, and add them to the vector store
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

# Check the status
print(f"File batch status: {file_batch.status}")
print(f"File counts: {file_batch.file_counts}")

# Create a new Assistant with File Search Enabled
assistant = client.beta.assistants.create(
    name="Document Search Assistant",
    instructions="You are an expert assistant. Use your knowledge base to answer questions about the provided documents.",
    model="gpt-3.5-turbo",
    tools=[{"type": "file_search"}],
)

# Update the Assistant to Use the New Vector Store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Create a Thread
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Can you find information on XYZ topic?",
        }
    ]
)

print(f"Thread tool resources: {thread.tool_resources.file_search}")

# Create a Run and Check the Output
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > {text}", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        print(f"\nassistant > {message.content}", flush=True)

# Stream the response
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()

# Close the file streams after processing
for stream in file_streams:
    stream.close()

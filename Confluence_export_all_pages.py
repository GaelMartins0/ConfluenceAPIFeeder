# Command to run the script (output_dir not required):
# python Confluence_export_all_pages.py --space_key 'spaceKey' --username 'username' --api_token 'password'

import requests
from requests.auth import HTTPBasicAuth
import os
import time
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
confluence_url = os.getenv('CONFLUENCE_URL')
if not confluence_url:
    raise ValueError("Confluence URL key not found. Please set the CONFLUENCE_URL environment variable.")

def get_all_pages_in_space(confluence_url, space_key, auth):
    page_size = 25
    start = 0
    all_pages = []
    
    while True:
        url = f"{confluence_url}/rest/api/content?spaceKey={space_key}&type=page&start={start}&limit={page_size}"
        response = requests.get(url, auth=auth)
        
        if response.status_code == 200:
            data = response.json()
            all_pages.extend(data['results'])
            if 'next' not in data['_links']:
                break
            start += page_size
        else:
            print(f"Failed to get pages. Status code: {response.status_code}")
            print(response.text)
            break

    return all_pages

def get_page_title(confluence_url, page_id, auth):
    page_url = f"{confluence_url}/rest/api/content/{page_id}"
    response = requests.get(page_url, auth=auth)
    
    if response.status_code == 200:
        page_data = response.json()
        return page_data.get('title', f"Confluence_Page_{page_id}")
    else:
        print(f"Failed to get page title for page ID {page_id}. Status code: {response.status_code}")
        print(response.text)
        return f"Confluence_Page_{page_id}"

def export_page_as_pdf(confluence_url, page_id, page_title, auth, output_dir):
    sanitized_title = "".join(c for c in page_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    export_url = f"{confluence_url}/spaces/flyingpdf/pdfpageexport.action?pageid={page_id}"
    response = requests.get(export_url, auth=auth)

    if response.status_code == 200:
        filename = f"{sanitized_title}_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"PDF exported successfully for page '{page_title}': {output_path}")
    else:
        print(f"Failed to export PDF for page '{page_title}'. Status code: {response.status_code}")
        print(response.text)

def clear_output_directory(output_dir):
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            print(f"Output directory '{output_dir}' is not empty. Deleting files...")
            for file in files:
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"All files deleted from '{output_dir}'")
        else:
            print(f"Output directory '{output_dir}' is empty.")
    else:
        os.makedirs(output_dir)
        print(f"Output directory '{output_dir}' created.")

def export_all_pages_in_space(confluence_url, space_key, username, api_token, output_dir):
    auth = HTTPBasicAuth(username, api_token)
    
    # Clear the output directory if not empty
    clear_output_directory(output_dir)
    
    pages = get_all_pages_in_space(confluence_url, space_key, auth)
    for page in pages:
        page_id = page['id']
        page_title = get_page_title(confluence_url, page_id, auth)
        export_page_as_pdf(confluence_url, page_id, page_title, auth, output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export all Confluence pages in a space to individual PDF files.')
    parser.add_argument('--space_key', required=True, help='Space key of the Confluence space')
    parser.add_argument('--username', required=True, help='Username for Confluence')
    parser.add_argument('--api_token', required=True, help='API token for Confluence')
    parser.add_argument('--output_dir', default='Docs', help='Directory to save PDF files (default: Docs)')

    args = parser.parse_args()
    
    export_all_pages_in_space(confluence_url, args.space_key, args.username, args.api_token, args.output_dir)

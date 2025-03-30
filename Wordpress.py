# ================= IMPORTS ==================
from dotenv import load_dotenv
import os
import base64
import requests
import json
from urllib.parse import urlparse

load_dotenv()

# ================= FUNCTIONS ==================

class WordpressHelper:
    # Setup function Establishes Auth&Connection to Site
    def __init__(self, client_name):
        """Initialize WordPress credentials from environment variables."""
        self.app_user = os.getenv(f'WP_APPLICATION_USERNAME_{client_name}')
        self.app_pass = os.getenv(f'WP_APPLICATION_PASSWORD_{client_name}')
        self.url = os.getenv(f'WP_URL_{client_name}')  # Fetch actual URL

        if not all([self.app_user, self.app_pass, self.url]):
            raise ValueError("Missing required environment variables for WordPress authentication.")

        self.creds = f"{self.app_user}:{self.app_pass}"
        token = base64.b64encode(self.creds.encode()).decode('utf-8')

        self.headers = {
            "Authorization": f'Basic {token}',
            "Content-Type": "application/json"
        }
        self.test_connection(client_name)

    # Function that verifes the connection to the wordpress site
    def test_connection(self, client_name):
        response = requests.get(f"{self.url}/wp-json/wp/v2", headers=self.headers)

        if response.status_code == 200:
            print(f"Connected To {client_name}")
            return True
        else:
            print(f"Failed to connect to {client_name}: {response.text}")
    
            return False
    
    # Determine whether the URL corresponds to a post or page and return the appropriate endpoint.
    def determine_endpoint(self, url):
        base = f"{self.url}/wp-json"
        # Extract the slug from the URL
        parsed_url = urlparse(url)
        slug = parsed_url.path.strip("/").split("/")[-1]

        # Try to fetch as a post first
        response = requests.get(f"{self.url}/wp-json/wp/v2/posts?slug={slug}", headers=self.headers)

        if response.status_code == 200 and response.json():
            return f"{base}/wp/v2/posts"

        # If not a post, try for a page
        response = requests.get(f"{self.url}/wp-json/wp/v2/pages?slug={slug}", headers=self.headers)

        if response.status_code == 200 and response.json():
            return f"{base}/wp/v2/pages" 
        
        types_response = requests.get(f"{base}/wp/v2/types", headers=self.headers)
        if types_response.status_code == 200:
            post_types = types_response.json().keys()  # Example: ['posts', 'pages', 'courses', ...]

            for post_type in post_types:
                response = requests.get(f"{base}/wp/v2/{post_type}?slug={slug}", headers=self.headers)
                if response.status_code == 200 and response.json():
                    return f"{base}/wp/v2/{post_type}"  # Return the matching CPT endpoint

        # Return None if no valid post or page is found
        print(f"Failed to determine type for URL {url}")
        return None

    # If no ID specified function takes url and returns ID
    def get_post_id_by_url(self, endpoint, data):
        try:
            url = data.get("url", None)
            # Extract the slug from URL
            parsed_url = urlparse(url)
            slug = parsed_url.path.strip("/").split("/")[-1]  # Extract last part of the path
            # Fetch post or page using the slug
            response = requests.get(f"{endpoint}?slug={slug}", headers=self.headers)
            
            if response.status_code != 200 or not response.json():
                print(f"Failed to fetch post ID for URL {url}: {response.status_code} - {response.text}")
                return None
            
            post_data = response.json()[0]
            return post_data.get("id", None)
        except:
            return None

    # Function fetches existing Meta associated with Page
    def get_existing_meta(self, endpoint, post_id):
        url = f"{endpoint}/{post_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Failed to fetch existing meta for {post_id}: {response.status_code} - {response.text}")
            return None
        
        existing_data = response.json()
        existing_meta = existing_data.get("meta", {})

        return existing_meta
    
    # Function Updates meta based on data/endpoint
    def update_meta_yoast_id(self, data):
        """Update Yoast SEO metadata for a post/page."""
        endpoint = self.determine_endpoint(data['url'])
        if endpoint is None:
            return False
        print(f"EP: {endpoint}")
        post_id = data.get("id", None)
        if post_id is None:
            post_id = self.get_post_id_by_url(endpoint, data)
            if post_id is None:
                print(f"No ID or URL for: {data}")
                return False

        existing_meta = self.get_existing_meta(endpoint, post_id)
        print(f"\n\n{existing_meta}")
        if existing_meta is None:
            return False  # Exit if metadata couldn't be retrieved

        # Preserve existing values if new ones are empty
        updated_meta = {
            "_yoast_wpseo_title": data.get("meta_title", existing_meta.get("_yoast_wpseo_title", "")),
            "_yoast_wpseo_metadesc": data.get("meta_description", existing_meta.get("_yoast_wpseo_metadesc", ""))
        }

        # Send update request
        update_payload = {
            "meta": updated_meta
        }
        
        url = f"{endpoint}/{post_id}"
        update_response = requests.put(url, json=update_payload, headers=self.headers)
        print(update_payload)
        print(url)
        print(f"\n\n{update_response.json()}")
        if update_response.status_code == 200:
            print(f"Successfully updated SEO metadata for {data['url']}")
            return True
        else:
            print(f"Update failed: {update_response.status_code} - {update_response.text}")
            return False
    

    
# ================= MAIN ==================
if __name__ == "__main__":
    client_name = "PREFTRAIN"
    smartgadgets = WordpressHelper(client_name)

    data = {
        "url": "https://www.preftrain.com.au/courses/telephone-de-escalation-techniques/",
        "meta_title": "Telephone De-Escalation Training Course | Get a Quote Today"
    }

    smartgadgets.update_meta_yoast_id(data)
    




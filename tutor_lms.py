import requests
import csv
import base64

# WordPress site details
WP_URL = "https://www.preftrain.com.au/"
API_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/courses"  # Check if 'courses' is the correct post type
USERNAME = "impressive"
APPLICATION_PASSWORD = "igUk ZNsq qmyj FBRm AzqQ OtiM"

# Encode authentication manually (Fixes issues with spaces in passwords)
auth_string = f"{USERNAME}:{APPLICATION_PASSWORD}"
auth_encoded = base64.b64encode(auth_string.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_encoded}",
    "Content-Type": "application/json"
}

# Function to update only meta description
def update_seo_meta(course_id, meta_description):
    data = {
        "meta": {
            "_yoast_wpseo_metadesc": meta_description  # Updating only meta description
        }
    }

    response = requests.put(f"{API_ENDPOINT}/{course_id}", json=data, headers=headers)  # Changed to PUT
    if response.status_code == 200:
        print(f"Updated SEO for Course ID {course_id}")
    else:
        print(f"Failed to update Course ID {course_id}: {response.text}")
# Function to get course ID by slug
def get_course_id(slug):
    response = requests.get(f"{API_ENDPOINT}?slug={slug}", headers=headers)  # Added headers
    if response.status_code == 200 and response.json():
        return response.json()[0]['id']
    else:
        print(f":warning: Course with slug '{slug}' not found.")
        return None
# Read CSV and update only meta descriptions
def process_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            course_slug = row["slug"].rstrip("/")  # Remove trailing slash if present
            meta_description = row["meta_description"]
            course_id = get_course_id(course_slug)
            if course_id:
                update_seo_meta(course_id, meta_description)
    
    
    update_seo_meta(course_id, meta_description)
# Run the script
if __name__ == "__main__":
    process_csv("desc.csv")
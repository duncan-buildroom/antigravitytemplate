import argparse
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file explicitly if needed, 
# though normally the agent environment or user shell should have them.
# We'll try to find a .env in the project root just in case.
# Load environment variables from .env file explicitly if needed.
# We'll try to find a .env in the scripts dir, the skill root, or the project root.
current_dir = os.path.dirname(os.path.abspath(__file__))
possible_env_paths = [
    os.path.join(current_dir, '.env'),
    os.path.join(os.path.dirname(current_dir), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(current_dir)), '.env')
]

for env_path in possible_env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

def scrape_branding(url):
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print(json.dumps({"error": "FIRECRAWL_API_KEY not found in environment variables."}))
        sys.exit(1)

    # Ensure API Key format is correct (sometimes 'fc-' is missing or duplicated in configs, specific logic can be added here if needed)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prepare the extraction schema for design details and assets
    extract_schema = {
        "type": "object",
        "properties": {
            "logo_url": {"type": "string", "description": "URL of the main brand logo"},
            "secondary_logo_url": {"type": "string", "description": "URL of secondary logo or icon if available"},
            "hero_image_url": {"type": "string", "description": "URL of the main hero image or representative brand image"},
            "button_styles": {
                "type": "object",
                "properties": {
                    "background_color": {"type": "string"},
                    "text_color": {"type": "string"},
                    "border_radius": {"type": "string", "description": "e.g., 4px, 50%, etc."},
                    "box_shadow": {"type": "string"},
                    "font_weight": {"type": "string"}
                },
                "description": "CSS styles for the primary call-to-action button"
            },
            "design_notes": {"type": "string", "description": "Description of general design vibe (e.g., glassmorphism, flat, material, brutalist) and any specific effects like gradients or textures."}
        },
        "required": ["logo_url"]
    }

    data = {
        "url": url,
        "formats": ["branding", "extract"],
        "extract": {
            "schema": extract_schema
        }
    }

    try:
        response = requests.post("https://api.firecrawl.dev/v2/scrape", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Process and download assets
        if 'data' in result:
            data_obj = result['data']
            extract_data = data_obj.get('extract', {})
            
            # Create assets directory
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            assets_dir = os.path.join(project_root, 'brand_assets', domain)
            os.makedirs(assets_dir, exist_ok=True)
            
            images_to_download = {}
            if extract_data and extract_data.get('logo_url'):
                images_to_download['logo'] = extract_data['logo_url']
            if extract_data and extract_data.get('secondary_logo_url'):
                images_to_download['secondary_logo'] = extract_data['secondary_logo_url']
            if extract_data and extract_data.get('hero_image_url'):
                images_to_download['hero'] = extract_data['hero_image_url']
                
            downloaded_paths = {}
            
            for name, img_url in images_to_download.items():
                if not img_url: continue
                try:
                    # Handle relative URLs if necessary (though Firecrawl usually returns absolute)
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        # rudimentary relative path handling
                        parsed_base = urlparse(url)
                        img_url = f"{parsed_base.scheme}://{parsed_base.netloc}{img_url}"
                        
                    img_resp = requests.get(img_url, timeout=10)
                    img_resp.raise_for_status()
                    
                    # Guess extension from url or content-type
                    ext = 'png'
                    if 'jpeg' in img_resp.headers.get('Content-Type', ''): ext = 'jpg'
                    elif 'svg' in img_resp.headers.get('Content-Type', ''): ext = 'svg'
                    elif img_url.lower().endswith('.png'): ext = 'png'
                    elif img_url.lower().endswith('.jpg') or img_url.lower().endswith('.jpeg'): ext = 'jpg'
                    elif img_url.lower().endswith('.svg'): ext = 'svg'
                    
                    filename = f"{name}.{ext}"
                    file_path = os.path.join(assets_dir, filename)
                    
                    with open(file_path, 'wb') as f:
                        f.write(img_resp.content)
                    
                    downloaded_paths[name] = file_path
                except Exception as img_err:
                    # Don't fail the whole script if an image fails
                    downloaded_paths[name] = f"Failed to download: {str(img_err)}"

            # Enrich the output with local paths
            result['data']['local_assets'] = downloaded_paths

        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
             error_msg = e.response.text
        print(json.dumps({"error": f"API Request failed: {error_msg}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape branding from a URL using Firecrawl.")
    parser.add_argument("url", help="The URL to scrape.")
    args = parser.parse_args()
    
    scrape_branding(args.url)

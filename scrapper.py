from rembg import remove
from PIL import Image
import os

async def save_image(path):
    try:
        input = Image.open(path)
        output = remove(input)
        file_name=os.path.basename(path).split(".")[0]
        file_path=f"images/{file_name}.png"
        output.save(file_path)
        os.remove(path)
    except Exception as e:
        print(e)
        pass


    

# output.save("output.png")
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image

async def download_images(url,name, folder="images", min_width=800, min_height=800):
    # Create folder
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Get webpage content
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch page")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract image tags
    img_tags = soup.find_all("img")

    print(f"Found {len(img_tags)} images")

    downloaded_count = 0
    
    for i, img in enumerate(img_tags):
        img_url = img.get("src")

        if not img_url:
            continue

        # Convert relative URLs to absolute
        img_url = urljoin(url, img_url)

        try:
            # Download image data
            img_data = requests.get(img_url, headers=headers).content
            
            # Check image size using PIL
            with BytesIO(img_data) as img_buffer:
                pil_img = Image.open(img_buffer)
                width, height = pil_img.size
                
                # Check if image meets size requirement
                if (width >= min_width and height >= min_height) or (width*height >= min_width*min_height):
                    file_path = os.path.join(folder, f"{name}.jpg")
                    
                    with open(file_path, "wb") as f:
                        f.write(img_data)
                    
                    print(f"Downloaded: {file_path} (Size: {width}x{height})")
                    break
                else:
                    print(f"Skipped: {img_url} (Size: {width}x{height} - below {min_width}x{min_height})")

        except Exception as e:
            print(f"Failed: {img_url} | Error: {e}")

    print(f"\nDownloaded {downloaded_count} images (filtered by minimum size {min_width}x{min_height})")

# 🔹 Example usage
if __name__ == "__main__":
    # website_url = "https://www.archanaskitchen.com/besan-ka-pitta-recipe-in-hindi"
    # download_images(website_url,"besan-ka-pitta", min_width=800, min_height=800)
    save_image("images/1834.jpg")
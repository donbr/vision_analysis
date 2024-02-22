import base64
import imghdr
import io
import requests
import PIL.Image
import exifread
import hachoir.metadata
import hachoir.parser

def encode_image_from_file(image_path: str) -> str:
    """Encode image to a base64 string from a given file path."""
    try:
        if imghdr.what(image_path) is None:
            return "Provided file is not a valid image."

        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: Image file not found."
    except Exception as e:
        return f"Error reading the image file: {e}"

def encode_image_from_url(image_url: str) -> str:
    """Encode image to a base64 string fetched from a URL."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()  
        encoded_image = base64.b64encode(response.content).decode('utf-8')
        return encoded_image
    except requests.exceptions.HTTPError:
        return f"Error: HTTP request failed with status code {response.status_code}."
    except requests.exceptions.RequestException:
        return "Error: Failed to fetch the image due to a network error."

def display_base64_image(base64_image: str, alt_text: str = "Base64 Encoded Image", style: str = "") -> str:
    """Display a base64-encoded image in a Jupyter notebook or IPython environment."""
    full_src_str = f"data:image/jpeg;base64,{base64_image}"
    html_str = f'<img src="{full_src_str}" alt="{alt_text}" style="{style}" />'
    return html_str

def extract_pil_metadata(encoded_image):
    metadata = {}

    try:
        image_data = base64.b64decode(encoded_image)
        with PIL.Image.open(io.BytesIO(image_data)) as img:
            metadata['PIL'] = { 
                'width': img.size[0],
                'height': img.size[1],
                'format': img.format,
                'exif': img._getexif()  
            }

    except (PIL.UnidentifiedImageError, ValueError) as e:
        metadata['error'] = f"Image decoding error: {e}"
    except Exception as e:
        metadata['error'] = f"Unexpected error during processing: {e}"

    return metadata

def extract_exifread_metadata(encoded_image):
    metadata = {}

    try:
        image_data = base64.b64decode(encoded_image)
        metadata['ExifRead'] = exifread.process_file(io.BytesIO(image_data), details=True) 

    except Exception as e: 
        metadata['error'] = str(e)

    return metadata

def extract_hachoir_metadata(encoded_image):
    metadata = {}

    try:
        image_data = base64.b64decode(encoded_image)
        parser = hachoir.parser.createParser(io.BytesIO(image_data))  
        metadata_hachoir = hachoir.metadata.extractMetadata(parser)
        metadata['Hachoir'] = metadata_hachoir.exportPlaintext() 

    except Exception as e:  
        metadata['error'] = str(e)

    return metadata

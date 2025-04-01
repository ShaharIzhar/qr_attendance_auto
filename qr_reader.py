import cv2
from pyzbar.pyzbar import decode
import webbrowser
import pdb

def is_url(data):
    return data.startswith("http://") or data.startswith("https://")

def detect_barcode_from_image(image_path):
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Failed to load image: {image_path}")
        return

    # Decode barcodes
    barcodes = decode(image)

    for barcode in barcodes:
        data = barcode.data.decode('utf-8')
        print("📦 Data:", data)

        if is_url(data):
            webbrowser.open(data)

# Example usage
detect_barcode_from_image("./barcode_test.jpg")
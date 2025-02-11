import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageFilter, ImageOps

# Set up Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    """
    image = image.convert("L")  # Convert to grayscale
    image = image.filter(ImageFilter.MedianFilter())  # Reduce noise
    image = ImageOps.autocontrast(image)  # Enhance contrast
    return image

def crop_image(image, crop_region):
    """
    Crop the image to the specified region.
    crop_region: Tuple (x, y, width, height).
    """
    x, y, width, height = crop_region
    return image.crop((x, y, x + width, y + height))

def get_incremented_filename(base_path):
    """
    Increment the filename if a file with the same name already exists.
    """
    base_name, ext = os.path.splitext(base_path)
    counter = 1
    new_path = base_path
    while os.path.exists(new_path):
        new_path = f"{base_name}-{counter}{ext}"
        counter += 1
    return new_path

def extract_text_from_pdf(pdf_path, output_txt_path, crop_region):
    """
    Extract text from a cropped region of a PDF and save it to a .txt file.
    The cropped region is also saved as a .png file.
    """
    # Path to Poppler binaries
    poppler_path = r"C:\poppler-24.08.0\Library\bin"  # Adjust based on your installation
    # Convert PDF pages to images using high DPI
    images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    
    extracted_text = ""
    for idx, image in enumerate(images):
        # Preprocess the image
        processed_image = preprocess_image(image)
        # Crop the image to the specified region
        cropped_image = crop_image(processed_image, crop_region)
        # Save the cropped region as a .png file
        cropped_image_path = get_incremented_filename(f"cropped_page_{idx + 1}.png")
        cropped_image.save(cropped_image_path)
        print(f"Cropped image saved to {cropped_image_path}")
        # Extract text from the cropped region
        text = pytesseract.image_to_string(
            cropped_image, 
            lang="eng", 
            config="--oem 1 --psm 6"
        )
        extracted_text += text + "\n"
    
    # Get incremented filename if needed
    output_txt_path = get_incremented_filename(output_txt_path)
    
    # Save the extracted text to a .txt file
    with open(output_txt_path, "w", encoding="utf-8") as file:
        file.write(extracted_text)
    
    return output_txt_path

# Replace these paths and region with your PDF file, desired output location, and crop region
pdf_path = r"C:\Users\Chev\Documents\IMG_20250106_0002.pdf"
output_txt_path = r"C:\Users\Chev\Documents\extracted_text.txt"
crop_region = (500, 340, 600, 350)  # (x, y, width, height) - Adjust as needed

# Extract text from the PDF and save to a file
try:
    final_output_path = extract_text_from_pdf(pdf_path, output_txt_path, crop_region)
    print(f"Text has been successfully extracted and saved to {final_output_path}")
except Exception as e:
    print(f"An error occurred: {e}")

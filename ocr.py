from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set up Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path, output_txt_path):
    # Provide the path to the Poppler binaries
    poppler_path = r"C:\poppler-24.08.0\Library\bin"  # Adjust if you extracted Poppler elsewhere
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image) + "\n"
    
    # Save the extracted text to a .txt file
    with open(output_txt_path, "w", encoding="utf-8") as file:
        file.write(text)
    
    return text

# Replace with the path to your PDF and desired output .txt file
pdf_path = r"C:\Users\Chev\Documents\IMG_20250106_0002.pdf"
output_txt_path = r"C:\Users\Chev\Documents\extracted_text.txt"

text = extract_text_from_pdf(pdf_path, output_txt_path)
print(f"Text has been extracted and saved to {output_txt_path}")

# text = extract_text("C:/Users/Chev/Documents/IMG_20250106_0002.pdf");
from flask import Flask, request, jsonify, send_file
import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageFilter, ImageOps
import json
from flask_cors import CORS
import subprocess


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

# Detect OS and set paths
# if os.name == "nt":  # Windows
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
# poppler_path = r"\app\poppler-24.08.0\Library\bin"

# Add poppler to PATH
poppler_path = "/app/poppler-24.08.0/Library/bin"
os.environ["PATH"] += os.pathsep + poppler_path

# Verify if Poppler tools are accessible
def check_poppler():
    try:
        result_pdftotext = subprocess.run(["which", "pdftotext"], capture_output=True, text=True)
        result_pdftoppm = subprocess.run(["which", "pdftoppm"], capture_output=True, text=True)

        return {
            "pdftotext_path": result_pdftotext.stdout.strip(),
            "pdftoppm_path": result_pdftoppm.stdout.strip()
        }

    except Exception as e:
        return {"error": str(e)}

@app.route('/poppler', methods=['GET'])
def poppler():
    print("checking poppler")
    result = check_poppler()
    return jsonify(result)  # ✅ Return a JSON response

@app.route('/tesseract', methods=['GET'])
def tesseract():
    print("checking tessseract")
    tesseract_path = "/usr/bin/tesseract"
    print(f"Tesseract Path: {tesseract_path}")
    print(f"File exists: {os.path.exists(tesseract_path)}")
    print(f"Is executable: {os.access(tesseract_path, os.X_OK)}")

    os.system(f"{tesseract_path} --version")
    result = check_tesseract()
    return result  # ✅ Return a JSON response

def check_tesseract():
    try:
        result = subprocess.run(["/usr/bin/tesseract", "--version"], capture_output=True, text=True)
        print(result.stdout.strip())
        return result.stdout.strip()
    except Exception as e:
        return {"error running tesseract": str(e)}
# else:  # Linux (Render)
#     pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
#     poppler_path = None  # No need to specify for Linux

def preprocess_image(image):
    image = image.convert("L")
    image = image.filter(ImageFilter.MedianFilter())
    image = ImageOps.autocontrast(image)
    return image

def crop_image(image, crop_region):
    x, y, width, height = crop_region
    cropped = image.crop((x, y, x + width, y + height))
    cropped.save("cropped-img.png")  # Save cropped image to local directory
    return cropped

def extract_text_from_pdf(pdf_path, crop_region):
    # poppler_path = r"C:\poppler-24.08.0\Library\bin"
    print("extracting")
    print("/app/poppler-24.08.0/Library/bin")
    print(r"/app/poppler-24.08.0/Library/bin")
    print("Updated PATH:", os.environ["PATH"])
    # images = convert_from_path(pdf_path, dpi=300, poppler_path="/app/poppler-24.08.0/Library/bin")
    images = convert_from_path(
        pdf_path, 
        dpi=300
    )

    print("i have the IMAGE now")
    extracted_text = ""
    for image in images:
        processed_image = preprocess_image(image)
        cropped_image = crop_image(processed_image, crop_region)
        text = pytesseract.image_to_string(cropped_image, lang="eng", config="--oem 1 --psm 6")
        extracted_text += text + "\n"
    return extracted_text

@app.route('/extract-text', methods=['POST'])
def extract_text():
    print("checking extracted")
    try:
        print( "im here")
        file = request.files['pdf']
        crop_region = json.loads(request.args.get('crop_region'))
        
        print( "i have the file")
        if not file or not crop_region:
            return jsonify({"error": "PDF file and crop_region are required"}), 400
        
        temp_pdf_path = "temp.pdf"
        file.save(temp_pdf_path)
        
        print( "i have the pdf path")
        
        extracted_text = extract_text_from_pdf(temp_pdf_path, crop_region)
        
        os.remove(temp_pdf_path)
        print(extracted_text)
        return jsonify({"extracted_text": extracted_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-cropped-image', methods=['GET'])
def get_cropped_image():
    print("checking cropped image")
    try:
        file_path = "cropped-img.png"  # Path to the cropped image
        return send_file(file_path, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.jinja_env.auto_reload = True
#     app.config["TEMPLATES_AUTO_RELOAD"] = True
#     app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT
    app.run(host="0.0.0.0", port=port)
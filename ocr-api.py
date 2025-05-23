from flask import Flask, request, jsonify, send_file
import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageFilter, ImageOps
import json
from flask_cors import CORS
import subprocess
import psycopg2
from psycopg2 import Binary
from io import BytesIO
from mimetypes import guess_type
from datetime import datetime


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
poppler_path = "/app/poppler-24.08.0/Library/bin"

if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    poppler_path = r"C:\poppler-24.08.0\Library\bin"

os.environ["PATH"] += os.pathsep + poppler_path

DATABASE_URL = "postgresql://ervy_brokerage_02_user:8Ni6rDYyFWfNRzEA6zq3N4xGm2wf8UAh@dpg-d0ctkhemcj7s73av1ifg-a.oregon-postgres.render.com/ervy_brokerage_02"

# Function to connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# API Endpoint to fetch movies
@app.route('/movies', methods=['GET'])
def get_movies():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vsm;")
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(movies)
    # Format response
    movie_list = [{"id": row[0], "label": row[1], "year": row[2]} for row in movies]
    return jsonify(movie_list)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdf']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_data = file.read()
    form = {
        "dsc_no": request.form.get('dsc_no'),
    }
    res = save_pdf_to_db(file_data, form)
    return res
    # print(request.form)


def save_pdf_to_db(file_data, form):
    print(form)
    print(form['dsc_no'])
    # conn = get_db_connection()
    # cur = conn.cursor()

    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS pdf_files (
    #         id SERIAL PRIMARY KEY,
    #         filename TEXT,
    #         file_data BYTEA
    #     )
    # """)
    # return
    # data = request.get_json()
    # print(data)
    dsc_no = form['dsc_no'] # data.get('dsc_no')

    if not dsc_no:
        return jsonify({'error': 'dsc_no is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM dsc WHERE dsc_no = %s", (dsc_no,))
    if cursor.fetchone():
        return jsonify({'message': 'DSC number already exists'}), 409

    print('im here')
    cursor.execute(
        "INSERT INTO dsc (dsc_no, file) VALUES (%s, %s)",
        (form['dsc_no'], Binary(file_data))
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'PDF uploaded and saved successfully'}), 200

@app.route('/save-dsc-info', methods=['POST'])
def save_dsc_info():
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    dsc_no = form['dsc_no'] # data.get('dsc_no')

    if not dsc_no:
        return jsonify({'error': 'dsc_no is required'}), 400

    cursor.execute("SELECT 1 FROM dsc WHERE dsc_no = %s", (dsc_no,))
    if cursor.fetchone():
        return jsonify({'message': 'DSC number already exists'}), 409
    
    cursor.execute("INSERT INTO dsc (dsc_no) VALUES (%s)", (dsc_no,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Data saved successfully'}), 200

@app.route('/save-dsc', methods=['POST'])
def save_dsc():
    dsc_no = request.form.get('dsc_no')
    dsc_vsm = request.form.get('vsm')
    dsc_area = request.form.get('area')
    dsc_date = request.form.get('dsc_date')

    file = request.files.get('dsc_file')
    file_data = file.read() if file else None
    file_name = file.filename if file else None
    print(file_name)
    sub_files = request.files.getlist('sub_dsc_files')
    if not dsc_no:
        return jsonify({'error': 'dsc_no is required'}), 400

    created_date = datetime.utcnow()
    modified_date = datetime.utcnow()

    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if dsc already exists
    cursor.execute("SELECT 1 FROM dsc WHERE dsc_no = %s", (dsc_no,))
    if cursor.fetchone():
        return jsonify({'message': 'DSC number already exists'}), 409
    # Insert main DSC with main file
    try:
        cursor.execute(
            """
            INSERT INTO dsc (dsc_no, vsm, area, dsc_date, file, file_name, created_date, modified_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (dsc_no, dsc_vsm, dsc_area, dsc_date, Binary(file_data), file_name, created_date, modified_date)
        )
    except Exception as e:
        print("❌ Error during INSERT:", e)
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    dsc_id = cursor.fetchone()[0]

    # Insert sub_dsc_files if provided
    for f in sub_files:
        cursor.execute(
            "INSERT INTO sub_dsc_files (dsc_id, filename, file_data) VALUES (%s, %s, %s)",
            (dsc_id, f.filename, Binary(f.read()))
        )

    conn.commit()
    return jsonify({'message': 'DSC saved successfully'}), 200
    # data = request.get_json()
    # print(data)
    # dsc_no = data.get('dsc_no')
    # dsc_vsm = data.get('dsc_vsm')
    # dsc_area = data.get('dsc_area')

    # if not dsc_no:
    #     return jsonify({'error': 'dsc_no is required'}), 400

    # conn = get_db_connection()
    # cursor = conn.cursor()
    # cursor.execute("SELECT 1 FROM dsc WHERE dsc_no = %s", (dsc_no,))
    # if cursor.fetchone():
    #     return jsonify({'message': 'DSC number already exists'}), 409
    
    # cursor.execute("INSERT INTO dsc (dsc_no, vsm, area) VALUES (%s, %s, %s)", (dsc_no, dsc_vsm, dsc_area,))
    # conn.commit()

    # return jsonify({'message': 'Number received successfully'}), 200
    # ---------------------------
    # if not data or 'name' not in data or 'description' not in data:
    #     return jsonify({'error': 'Missing required fields'}), 400
    
    # conn = get_db_connection()
    # cursor = conn.cursor()
    
    # try:
    #     cursor.execute("INSERT INTO dsc (dsc_no, area, vsm, dsc_date) VALUES (%s, %s, %s, %s)", (data['dsc_no'], data['area'], data['vsm'], data['dsc_date']))
    #     conn.commit()
    #     return jsonify({'message': 'DSC saved successfully'}), 201
    # except Exception as e:
    #     conn.rollback()
    #     return jsonify({'error': str(e)}), 500
    # finally:
    #     cursor.close()
    #     conn.close()
    # return jsonify({"succ": 'E'})
    
@app.route('/update-dsc', methods=['POST'])
def update_dsc():
    dsc_id = request.args.get('id')
    if not dsc_id:
        return jsonify({'error': 'DSC ID is required'}), 400

    dsc_no = request.form.get('dsc_no')
    dsc_vsm = request.form.get('vsm')
    dsc_area = request.form.get('area')
    dsc_date = request.form.get('dsc_date')

    file = request.files.get('dsc_file')
    file_data = file.read() if file else None
    file_name = file.filename if file else None

    sub_files = request.files.getlist('sub_dsc_files')
    modified_date = datetime.utcnow()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update core fields
        if file_data:
            cursor.execute("""
                UPDATE dsc 
                SET dsc_no=%s, vsm=%s, area=%s, dsc_date=%s,
                    file=%s, file_name=%s, modified_date=%s
                WHERE id=%s
            """, (dsc_no, dsc_vsm, dsc_area, dsc_date, Binary(file_data), file_name, modified_date, dsc_id))
        else:
            cursor.execute("""
                UPDATE dsc 
                SET dsc_no=%s, vsm=%s, area=%s, dsc_date=%s,
                    modified_date=%s
                WHERE id=%s
            """, (dsc_no, dsc_vsm, dsc_area, dsc_date, modified_date, dsc_id))

        # Optionally clear & re-insert sub_dsc_files
        if sub_files:
            cursor.execute("DELETE FROM sub_dsc_files WHERE dsc_id = %s", (dsc_id,))
            for f in sub_files:
                cursor.execute(
                    "INSERT INTO sub_dsc_files (dsc_id, filename, file_data) VALUES (%s, %s, %s)",
                    (dsc_id, f.filename, Binary(f.read()))
                )

        conn.commit()
        return jsonify({'message': 'DSC updated successfully'}), 200

    except Exception as e:
        conn.rollback()
        print("❌ Error during update:", e)
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/get-pdf', methods=['GET'])
def get_pdf():
    pdf_id = request.args.get('dsc_no')  # or use 'name'

    if not pdf_id:
        return jsonify({'error': 'Missing PDF ID'}), 400

    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT dsc_no, file FROM dsc WHERE dsc_no = %s", (pdf_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    print('done checking')
    if not row:
        return jsonify({'error': 'PDF not found'}), 404
    print('no row here')
    dsc_no, file = row

    if not file or len(file) == 0:
        return jsonify({'error': 'PDF file is empty'}), 400
    print('sending return anyway')
    # print(row)
    # Send the binary file back
    return send_file(
        io.BytesIO(file),
        mimetype='application/pdf',
        as_attachment=False,
        download_name=dsc_no
    )

@app.route('/delete-dsc', methods=['DELETE'])
def delete_dsc():
    dsc_id = request.args.get('id')

    if not dsc_id:
        return jsonify({'error': 'DSC ID is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dsc WHERE id = %s", (dsc_id,))
    conn.commit()

    return jsonify({'message': 'DSC deleted successfully'}), 200

@app.route('/get-dsc', methods=['GET'])
def get_dsc():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to get data from dsc table
    cursor.execute("SELECT id, dsc_no, area, vsm, dsc_date, file_name FROM dsc;")
    dsc = cursor.fetchall()

    # Query to get filenames from sub_dsc_files table
    cursor.execute("SELECT dsc_id, filename FROM sub_dsc_files;")
    sub_dsc_files = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert sub_dsc_files list into a dictionary for easy lookup
    sub_dsc_files_dict = {}
    for sub_dsc in sub_dsc_files:
        if sub_dsc[0] not in sub_dsc_files_dict:
            sub_dsc_files_dict[sub_dsc[0]] = []
        sub_dsc_files_dict[sub_dsc[0]].append(sub_dsc[1])
    
    # Build the response list including filenames from sub_dsc_files
    dsc_list = [{
        "id": row[0], 
        "dsc_no": row[1],
        "dsc_area": row[2],
        "dsc_vsm": row[3],
        "dsc_date": row[4],
        "file_name": row[5],
        "sub_dsc_files": sub_dsc_files_dict.get(row[0], []),  # Add corresponding sub_dsc_files
        "status": "Completed"
    } for row in dsc]
    
    return dsc_list

@app.route('/get-area', methods=['GET'])
def get_area():
    # CREATE TABLE area (
    # id SERIAL PRIMARY KEY,
    # name VARCHAR(100) NOT NULL
    # );
    print ('area list should be here')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM area;")
        area = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(area)
        area_list = [{"id": row[0], "name": row[1]} for row in area]
        return jsonify({ 
            "status": 200,
            "data": area_list 
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-vsm', methods=['GET'])
def get_vsm():
    # CREATE TABLE vsm (
    # id SERIAL PRIMARY KEY,
    # name VARCHAR(100) NOT NULL
    # );
    print ('vsm list should be here')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM vsm;")
        vsm = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(vsm)
        vsm_list = [
            { 
                "id": row[0], 
                "name": row[1]
            } for row in vsm]
        return jsonify({ 
            "status": 200,
            "data": vsm_list 
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-file', methods=['POST'])
def get_file():
    data = request.get_json()
    file_name = data.get('fileName')
    table = data.get('table')  # Get table name

    if not file_name or not table:
        return jsonify({'error': 'File name and table are required'}), 400

    # Connect to the database and retrieve the file data based on the file_name and table
    conn = get_db_connection()
    cursor = conn.cursor()

    if table == "dsc":
        file_column = "file"
        name_column = "file_name"
    elif table == "sub_dsc_files":
        file_column = "file_data"
        name_column = "filename"
    else:
        return jsonify({'error': 'Invalid table'}), 400
        
    try:
        cursor.execute(f"SELECT {file_column}, {name_column} FROM {table} WHERE {name_column} = %s", (file_name,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'File not found'}), 404

        file_data = result[0]
        file_name_from_db = result[1]

        # Determine MIME type
        mime_type, _ = guess_type(file_name_from_db)
        if not mime_type:
            mime_type = 'application/octet-stream'  # Default for binary files

        # Close the connection
        cursor.close()
        conn.close()

        # Return the file with the correct MIME type
        return send_file(
            BytesIO(file_data),
            as_attachment=True,
            download_name=file_name_from_db,
            mimetype=mime_type
        )

    except Exception as e:
        print(f"Error fetching file: {e}")
        cursor.close()
        conn.close()
        return jsonify({'error': 'Failed to fetch file from database'}), 500

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
    # images = convert_from_path(pdf_path, dpi=300, poppler_path="/app/poppler-24.08.0/Library/bin")
    images = convert_from_path(
        pdf_path, 
        dpi=300
    )

    extracted_text = ""
    for image in images:
        processed_image = preprocess_image(image)
        cropped_image = crop_image(processed_image, crop_region)
        text = pytesseract.image_to_string(cropped_image, lang="eng", config="--oem 1 --psm 6")
        extracted_text += text + "\n"
    return extracted_text

@app.route('/extract-text', methods=['POST'])
def extract_text():
    try:
        file = request.files['pdf']
        crop_region = json.loads(request.args.get('crop_region'))
        
        if not file or not crop_region:
            return jsonify({"error": "PDF file and crop_region are required"}), 400
        
        temp_pdf_path = "temp.pdf"
        file.save(temp_pdf_path)
        
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
import os
from flask import Flask, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
import utils_stego
import utils_watermark

app = Flask(__name__)

# Konfigurasi Folder
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 1. Handle File Upload
        if 'image_file' not in request.files:
            return "No file part", 400
        file = request.files['image_file']
        if file.filename == '':
            return "No selected file", 400

        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)

        # Ambil Input User
        stego_msg = request.form.get('stego_message', '')
        watermark_text = request.form.get('watermark_text', '')
        watermark_pos = request.form.get('watermark_pos', 'bottom_right')
        
        # Handle Logo Watermark Upload
        logo_file = request.files.get('watermark_logo')
        logo_path = None
        if logo_file and logo_file.filename != '':
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)

        # --- PROSES 1: STEGANOGRAFI ---
        stego_filename = f"stego_{os.path.splitext(filename)[0]}.png" # Harus PNG
        stego_output_path = os.path.join(app.config['RESULT_FOLDER'], stego_filename)
        
        try:
            if stego_msg:
                utils_stego.encode_lsb(original_path, stego_msg, stego_output_path)
            else:
                # Jika tidak ada pesan, copy saja gambar asli
                from PIL import Image
                Image.open(original_path).save(stego_output_path)
        except Exception as e:
            print(f"Stego Error: {e}")

        # --- PROSES 2: WATERMARKING ---
        wm_filename = f"wm_{os.path.splitext(filename)[0]}.png"
        wm_output_path = os.path.join(app.config['RESULT_FOLDER'], wm_filename)
        
        try:
            # Prioritas: Logo dulu, kalau kosong baru Text
            utils_watermark.apply_watermark(
                original_path, 
                wm_output_path, 
                text=watermark_text, 
                logo_path=logo_path, 
                position=watermark_pos,
                opacity=0.6
            )
        except Exception as e:
            print(f"Watermark Error: {e}")

        return render_template('index.html', 
                               original=filename,
                               stego=stego_filename,
                               watermark=wm_filename,
                               processed=True)

    return render_template('index.html', processed=False)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
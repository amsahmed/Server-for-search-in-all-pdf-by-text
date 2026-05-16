from flask import Flask, request, jsonify, send_file
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import os

app = Flask(__name__)

BASE_PATH = r"C:\Users\hp\Desktop"
SAVE_PATH = r"C:\Users\hp\Desktop\ACH_Results"  # هيتحفظ هنا

os.makedirs(SAVE_PATH, exist_ok=True)

@app.route('/search', methods=['POST'])
def search_ach():
    data = request.json
    ach_number = data.get('achNumber', '')

    if not ach_number:
        return jsonify({'success': False, 'error': 'achNumber مطلوب'}), 400

    for root, dirs, files in os.walk(BASE_PATH):
        for file_name in files:
            if not file_name.lower().endswith('.pdf'):
                continue
            file_path = os.path.join(root, file_name)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text() or ''
                        if ach_number in text:
                            # استخرج الصفحة وحفظها
                            reader = PdfReader(file_path)
                            writer = PdfWriter()
                            writer.add_page(reader.pages[page_num - 1])
                            
                            output_name = f"ACH_{ach_number}_page{page_num}.pdf"
                            output_path = os.path.join(SAVE_PATH, output_name)
                            
                            with open(output_path, 'wb') as f:
                                writer.write(f)
                            
                            # يبعت الملف مباشرة للتحميل
                            return send_file(
                                output_path,
                                as_attachment=True,
                                download_name=output_name
                            )
            except Exception:
                continue

    return jsonify({'success': False, 'error': 'الرقم مش موجود في أي ملف'}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
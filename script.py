from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import cv2
import numpy as np
import re
from typing import Dict, List, Tuple

app = Flask(__name__)
CORS(app)

reader = easyocr.Reader(['es', 'en'])

@app.route('/validate_data', methods=['POST'])
def validate_data():
    try:
        data = request.form
        file = request.files.get('file')
        

        if 'file' not in request.files or 'velocidad' not in data:
            return jsonify({'error': 'Entrada inválida'}), 400

        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        result = reader.readtext(img)
        extracted_text = " ".join([text for (_, text, _) in result])

        print(f"Texto extraído de la imagen: {extracted_text}")

        grouped_data = group_extracted_data(extracted_text)
        validation_result = validate_form_data(data, grouped_data)

        return jsonify({'validation_result': validation_result, 'grouped_data': grouped_data})
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

def group_extracted_data(text: str) -> Dict[str, str]:
    sections = {}
    lines = text.splitlines()
    
    patterns = {
        'Velocidad': r'Velocidad\s*([\d\s,.]+)',
        'Aceleracion': r'Aceleracion\s*([\d\s,.]+)',
        'Pasos por bolsa': r'Pasos\s*por\s*bolsa\s*([\d\s,.]+)'
    }
    
    for line in lines:
        for title, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                sections[title] = match.group(1).strip()

    return sections

def validate_form_data(form_data: Dict[str, str], extracted_data: Dict[str, str]) -> Dict[str, Union[str, List[str]]]:
    errors = []
    patterns = {
        'velocidad': r'([\d,.]+)',
        'aceleracion': r'([\d,.]+)',
        'pasos_por_bolsa': r'([\d]+)'
    }

    for key, pattern in patterns.items():
        expected_value = form_data.get(key)
        extracted_value = extracted_data.get(key.capitalize())
        
        if expected_value and extracted_value:
            expected_match = re.search(pattern, expected_value)
            extracted_match = re.search(pattern, extracted_value)
            
            if expected_match and extracted_match:
                if expected_match.group(1) != extracted_match.group(1):
                    errors.append(f"{key} no coincide: se esperaba {extracted_value}, pero se recibió {expected_value}")
            else:
                errors.append(f"Formato inválido para {key}")
        elif extracted_value is None:
            errors.append(f"No se encontró {key} en los datos extraídos")

    return {
        'status': 'éxito' if not errors else 'error',
        'errores': errors
    }

if __name__ == '__main__':
    app.run(port=5001, debug=True)

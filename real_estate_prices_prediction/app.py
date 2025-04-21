from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Загрузка модели
model = joblib.load('best_model.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        prediction = model.predict([data['features']])
        return jsonify({'prediction': prediction[0]})
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'error': 'Произошла ошибка на сервере'}), 500

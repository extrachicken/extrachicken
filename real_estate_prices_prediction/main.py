import os
from data_processing import load_and_process_data
from data_analysis import analyze_data
from model_training import train_and_save_model
from app import app

def main():
    # Путь к файлу данных
    data_file_path = 'data.csv'  # Убедитесь, что у вас есть этот файл

    # Шаг 1: Обработка данных
    print("Обработка данных...")
    X_train, X_test, y_train, y_test = load_and_process_data(data_file_path)

    # Шаг 2: Анализ данных
    print("Анализ данных...")
    analyze_data(data_file_path)

    # Шаг 3: Обучение и сохранение модели
    print("Обучение и сохранение модели...")
    train_and_save_model(X_train, y_train, X_test, y_test)

    # Шаг 4: Запуск API
    print("Запуск API...")
    app.run(debug=False)

if __name__ == '__main__':
    main()

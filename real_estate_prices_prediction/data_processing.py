import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_process_data(file_path):
    # Загрузка данных
    data = pd.read_csv(file_path)
    data.head()

    # Очистка данных
    data = data.dropna()  # Удаление пропущенных значений
    
    # Разделение данных на признаки и целевую переменную
    X = data.drop('price', axis=1)
    y = data['price']
    
    # Разделение на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test



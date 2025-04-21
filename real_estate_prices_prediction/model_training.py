from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib


def train_and_save_model(X_train, y_train, X_test, y_test):
    # Создание и обучение модели
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Оценка модели
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f'Random Forest MSE: {mse}')
    
    # Сохранение модели
    joblib.dump(model, 'best_model.joblib')
    print("Модель сохранена в файл best_model.joblib")

import pandas as pd
from sklearn.model_selection import train_test_split

data = pd.read_csv('data.csv')
data.head()

    # Очистка данных
data = data.dropna()  # Удаление пропущенных значений
    
    # Разделение данных на признаки и целевую переменную
X = data.drop('price', axis=1)
y = data['price']
    
# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_and_save_model(X_train, y_train, X_test, y_test)
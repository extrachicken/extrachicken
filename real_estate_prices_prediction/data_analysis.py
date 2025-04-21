import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(file_path):
    # Загрузка данных
    data = pd.read_csv(file_path)
    
    # Описательная статистика
    print(data.describe())
    
    # Визуализация распределения цен
    plt.figure(figsize=(10, 6))
    sns.histplot(data['price'], bins=30, kde=True)
    plt.title('Распределение цен на недвижимость')
    plt.xlabel('Цена')
    plt.ylabel('Частота')
    plt.show()
    
    # Визуализация корреляционной матрицы
    plt.figure(figsize=(12, 8))
    sns.heatmap(data.corr(), annot=True, fmt=".2f")
    plt.title('Корреляционная матрица')
    plt.show()

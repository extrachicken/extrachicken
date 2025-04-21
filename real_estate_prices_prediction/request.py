import requests

print("Введите: количество спален, количество ванных комнат, sqft_living, sqft_lot, количество этажей, есть ли рядом море(1-да, 0-нет), вид из окна(1-5), состояние дома(1-5)")
bedrooms, bathrooms, sqft_living, sqft_lot, floors, waterfront, view, condition = map(int, input().split())

url = 'http://127.0.0.1:5000/predict'
data = {
    "features": [bedrooms, bathrooms, sqft_living, sqft_lot, floors, waterfront, view, condition]  # Замените на ваши реальные значения
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print('Предсказание:', response.json()['prediction'])
else:
    print('Ошибка:', response.status_code)

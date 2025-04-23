from bs4 import BeautifulSoup
import requests

# Получаем содержимое веб-страницы
response = requests.get('https://parsinger.ru/2.1/DOM/example.html')
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Комбинированный поиск: ищем все абзацы с классом "my_class" и атрибутом "data-example"
paragraphs = soup.select('p.my_class[data-example]')

# Выводим найденные элементы
for p in paragraphs:
    print(f'Найденный элемент: {p.text}')
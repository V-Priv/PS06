import requests
from bs4 import BeautifulSoup
import csv


def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()  # Проверяем успешность запроса
    return response.text


def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    lamps = []

    for lamp in soup.select('div.WdR1o'):
        name = lamp.select_one('div.lsooF span')
        price = lamp.select_one('div.pY3d2 span')
        link = lamp.select_one('a[href]')

        if link:
            link = requests.compat.urljoin("https://divan.ru", link['href'])

        lamps.append({
            'name': name.get_text(strip=True) if name else None,
            'price': price.get_text(strip=True) if price else None,
            'link': link
        })

    return lamps


def get_next_page(soup):
    next_page = soup.select_one('a.next')
    if next_page and next_page.has_attr('href'):
        return requests.compat.urljoin("https://divan.ru", next_page['href'])
    return None


def save_to_csv(data, filename='lamps.csv'):
    if not data:
        return  # Не сохраняем пустой файл

    # Определяем названия столбцов
    fieldnames = ['Название товара', 'Цена', 'Ссылка на товар']

    # Преобразуем данные в соответствующий формат
    formatted_data = [
        {'Название товара': item['name'], 'Цена': item['price'], 'Ссылка на товар': item['link']}
        for item in data
    ]

    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(formatted_data)


def main():
    start_url = "https://www.divan.ru/category/svet"
    all_lamps = []

    current_url = start_url
    while current_url:
        html_content = fetch_page(current_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        lamps = parse_page(html_content)
        all_lamps.extend(lamps)

        current_url = get_next_page(soup)  # Получаем URL следующей страницы

    save_to_csv(all_lamps)


if __name__ == '__main__':
    main()
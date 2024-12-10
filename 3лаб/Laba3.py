import sqlite3
import requests

# Создание базы данных и таблицы posts
conn = sqlite3.connect('Laba3.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        body TEXT
    )
''')
conn.commit()

# Получение данных с сервера
url = 'https://jsonplaceholder.typicode.com/posts'
response = requests.get(url)

if response.status_code == 200:
    posts = response.json()
else:
    print(f"Ошибка при выполнении запроса: {response.status_code}")

# Сохранение данных в базу данных
for post in posts:
    cursor.execute('''
        INSERT OR IGNORE INTO posts (id, user_id, title, body)
        VALUES (?, ?, ?, ?)
    ''', (post['id'], post['userId'], post['title'], post['body']))

conn.commit()
print("Данные успешно сохранены в базу данных.")

# Чтение данных из базы
def get_posts_by_user(user_id):
    cursor.execute('''
        SELECT * FROM posts WHERE user_id = ?
    ''', (user_id,))
    
    posts = cursor.fetchall()
    
    if posts:
        for post in posts:
            print(f"ID: {post[0]}, User ID: {post[1]}, Title: {post[2]}, Body: {post[3]}")
    else:
        print(f"Постов для пользователя с ID {user_id} не найдено.")

get_posts_by_user(7)

conn.close()

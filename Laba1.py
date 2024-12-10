import requests

#GET-запрос
url = "https://jsonplaceholder.typicode.com/posts"
posts = requests.get(url)
posts_json = posts.json()
for i in posts_json:
    if (i["userId"] % 2 == 0):
        print(i, "\n")

#POST-запрос
new_data = {
"title": 'Тестовый пост',
}
post_response = requests.post(url, json=new_data)
print(post_response.json())

#PUT-запрос
updated_data= {
"title": 'Обновленный пост'
}
posts_put_response = requests.put(f"{url}/100", json=updated_data)
print(posts_put_response.json())
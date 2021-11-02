#!/usr/bin/env python3

import requests
import time

login = {
        'username': 'Loskarlos',
        'password': 'JednohoDneOvladnuKSI'
}

login1_url = "https://losoviny.iamroot.eu/part_one_login"
login2_url = "https://losoviny.iamroot.eu/part_two_login"

part_one = "https://losoviny.iamroot.eu/part_one"
part_two = "https://losoviny.iamroot.eu/part_two"

session1 = requests.Session()
post_response = session1.post(login1_url, data=login)
auth = post_response.json()
time.sleep(2)
headers = {"Authorization": f"Bearer {auth['auth_token']}"}

get_response = session1.get(part_one, headers=headers)
print(get_response.text)

session2 = requests.Session()
post_response = session2.post(login2_url, data=login)
time.sleep(2)
# headers = {"Authorization": f"Bearer {auth['auth_token']}"}

get_response = session2.get(part_two)
print(get_response.text)

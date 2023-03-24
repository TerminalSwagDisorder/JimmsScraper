import requests

# Make a request to a website
url = 'https://www.jimms.fi'
response = requests.get(url)

# Get the cookie from the response headers
cookie = response.cookies.get_dict()

# Get the user-agent from the request headers
user_agent = response.request.headers['User-Agent']

# Print the cookie and user-agent
print('Cookie:', cookie)
print('User-Agent:', user_agent)
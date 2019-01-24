import requests
from requests_oauthlib import OAuth2Session
import random
import string

def generateRandomString(string_length):
    """Return a randomly generated alphanumeric string of string_length length

    :string_length: length of the string to be created
    :returns: randomly generated string of length string_length

    """
    alpha_numer=string.ascii_letters + string.digits
    
    # concatenate string_length alphanumeric characters
    ret=''.join(random.SystemRandom().choice(alpha_numer) for _ in range(string_length))
    return ret

course_code = raw_input("enter the course code to be fetched: ")
assign_num = raw_input("enter assignment number to be fetched: ")
padded_assign_num = assign_num if (int(assign_num) > 9) else "0"+assign_num
course_site = {'MAT101': 'https://www.math.school.ca/course/Prob_Set_'+ padded_assign_num + '.pdf'}

if (not course_code in course_site.keys()):
    print("please enter a defined course or add one, defined courses:")
    for course in course_site:
        print(course)
    quit()

assign_url = course_site[course_code]
assign_req = requests.get(assign_url, allow_redirects=True)
if (assign_req.status_code == 200):
    open('q'+assign_num+".pdf", 'wb').write(assign_req.content)
    print("successfully downloaded!")
else:
    print("assignment %s does not exist" % assign_num)
    quit()

# credentials
client_id = 'client id from application'
client_secret = 'client secret from application'
redirect_uri = 'http://localhost:8888/callback'
local_state = generateRandomString(16)

# oAuth2 session
# redirect with params
oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, state=local_state)

# note requests takes reponsibility for forming the query string in the URI. The full URL looks like
# https://www.wunderlist.com/oauth/authorize?client_id=client_id&redirect_uri=redirect_uri&state=state
authorization_url, state = oauth.authorization_url('https://www.wunderlist.com/oauth/authorize')

print('Please authorize access at: %s' % authorization_url)

state = raw_input('Enter the state param from the callback URL')

if ( state != local_state ):
    print("authorization error, state mismatch.")
    quit()

code = raw_input('Enter the code param from the callback URL:')

tok_data = {'client_id': client_id, 'client_secret': client_secret, 'code': code}
token = requests.post('https://www.wunderlist.com/oauth/access_token', data=tok_data)

# retrieve access token from JSON
access_token = token.json()['access_token']

# Wundelrlist requires this for requests which require authentication
headers = {'X-Access-Token': access_token, 'X-Client-ID': client_id}

# create a task
list_id = 367927829
# optional parameters available are:
# assignee_id (int)
# completed (bool)
# recurrence_type (str): "day", "week", "month", "year"
# recurrence_count (int): >=1, accompanied by recurrence_type
# due_date (str): ISO8601 format date
# starred (bool)
post_data = {"list_id": list_id, "title": course_code + " assignment " + assign_num}
post_req = requests.post('https://a.wunderlist.com/api/v1/tasks', headers=headers, json=post_data)
if (post_req.status_code == 201):
    print("successfully added task!")
else:
    print("problem creating task, code:" + post_req.status_code)

import os
import unittest
import json
import requests

from requests_oauthlib import OAuth2Session

CLIENT_ID = os.environ.get("CLIENT_ID", None) or input("Ented your client ID:")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None) or input("Enter your client secret:")
SERVER_TOKEN = os.environ.get("SERVER_TOKEN", None) or input("Enter your server token:")


class TestHMRC(unittest.TestCase):
    def test_hello_world(self):
        g = requests.get("https://api.service.hmrc.gov.uk/hello/world", headers={"accept": "application/vnd.hmrc.1.0+json"})
        self.assertEquals(g.status_code, 200)
        self.assertEquals(json.loads(g.content.decode())['message'], 'Hello World')

    def test_hello_application(self):
        g = requests.get("https://api.service.hmrc.gov.uk/hello/application",
                         headers={
                             "accept": "application/vnd.hmrc.1.0+json",
                             "authorization": "Bearer {}".format(SERVER_TOKEN),
                         })
        self.assertEquals(g.status_code, 200)

    def test_hello_user(self):
        g = requests.get("https://api.service.hmrc.gov.uk/hello/user", headers={"accept": "application/vnd.hmrc.1.0+json"})
        self.assertEquals(g.status_code, 401)  # will require to authenticate

        hmrc = OAuth2Session(CLIENT_ID, scope="hello", redirect_uri="https://example.com/redirect")
        authorization_url, state = hmrc.authorization_url("https://api.service.hmrc.gov.uk/oauth/authorize")
        print("Please go here and authorize: {}".format(authorization_url))

    def test_hello_user_callback(self):
        redirect_response = input('Paste the full redirect URL here: ')

        hmrc_callback = OAuth2Session(CLIENT_ID, scope="hello", redirect_uri="https://example.com/redirect")
        token = hmrc_callback.fetch_token("https://api.service.hmrc.gov.uk/oauth/token",
                                          client_secret=CLIENT_SECRET,
                                          authorization_response=redirect_response)

        g = hmrc_callback.get("https://api.service.hmrc.gov.uk/hello/user", headers={"accept": "application/vnd.hmrc.1.0+json"})
        self.assertEquals(g.status_code, 200)

    def test_self_assessment(self):
        hmrc = OAuth2Session(CLIENT_ID, scope="read:self-assessment", redirect_uri="https://example.com/redirect")
        authorization_url, state = hmrc.authorization_url("https://api.service.hmrc.gov.uk/oauth/authorize")
        print("Please go here and authorize: {}".format(authorization_url))

        redirect_response = input('Paste the full redirect URL here: ')
        token = hmrc.fetch_token("https://api.service.hmrc.gov.uk/oauth/token",
                                 client_secret=CLIENT_SECRET,
                                 authorization_response=redirect_response)

        g = hmrc.get("https://api.service.hmrc.gov.uk/self-assessment", headers={"accept": "application/vnd.hmrc.1.0+json"})
        print(g.content)
        self.assertEquals(g.status_code, 200)

if __name__ == '__main__':
    unittest.main()

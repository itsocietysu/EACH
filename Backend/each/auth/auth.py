from each.auth.config import CONFIG, PROVIDER

import urllib.request
import json

def Configure(**kwargs):
    CONFIG.update(kwargs)

def Validate(token, provider):
    try:
        response = urllib.request.urlopen(CONFIG[provider]['check_token_url'] + token)
        certs = response.read().decode()
        json_load = json.loads(certs)
        return None, json_load['access_type'], json_load['email']
    except Exception as e:
        return str(e), None, None

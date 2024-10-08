from flask import Blueprint, request, redirect, session, url_for, current_app as app
import requests
import time

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    auth_url = (app.config['IG_AUTH_URL']
                + '?enable_fb_login=0&force_authentication=1&response_type=code'
                + '&client_id=' + app.config['IG_CLIENT_ID']
                + '&redirect_uri=' + app.config['IG_REDIRECT_URI']
                + '&scope=instagram_business_basic,instagram_business_content_publish,instagram_business_manage_comments')
    
    return redirect(auth_url) 

@auth.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: Code not provided by Instagram", 400

    short_token_url = app.config['IG_ACCESS_TOKEN_URL']
    short_payload = {
        'client_id': app.config['IG_CLIENT_ID'],
        'client_secret': app.config['IG_CLIENT_SECRET'],
        'grant_type': 'authorization_code',
        'redirect_uri': app.config['IG_REDIRECT_URI'],
        'code': code
    }

    short_response = requests.post(short_token_url, data=short_payload)
    if short_response.status_code != 200:
        return f"Failed to fetch short access token. Response: {short_response.text}", 400

    short_lived_token = short_response.json().get('access_token')

    long_token_url = app.config['IG_GRAPH_API_URL'] + '/access_token'
    long_payload = {
        'grant_type': 'ig_exchange_token',
        'client_secret': app.config['IG_CLIENT_SECRET'],
        'access_token': short_lived_token
    }

    long_response = requests.get(long_token_url, params=long_payload)
    if long_response.status_code != 200:
        return f"Failed to fetch long access token. Response: {long_response.text}", 400

    long_response = long_response.json()
    session['access_token'] = long_response.get('access_token')
    session['expires_in'] = long_response.get('expires_in')
    session['token_created_at'] = int(time.time())

    return redirect(url_for('home.bio_page'))

@auth.route('/refresh')
def refresh():
    
    token_url = app.config['IG_GRAPH_API_URL'] + '/refresh_access_token'
    payload = {
        'access_token': session.get('access_token'),
        'grant_type': 'ig_refresh_token'
    }

    response = requests.get(token_url, params=payload)
    if response.status_code != 200:
        return f"Failed to refresh access token. Response: {response.text}", 400

    response = response.json()
    session['access_token'] = response.get('access_token')
    session['expires_in'] = response.get('expires_in')
    session['token_created_at'] = int(time.time())

    return {'message': 'Success', 'token': response.get('access_token')}
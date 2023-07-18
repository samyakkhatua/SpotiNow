from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import requests
import time
from typing import Dict
from base64 import b64encode
import base64
import secrets
import string



app = FastAPI()

@app.get("/")
def read_root():
    return {"Welcome to Spotinow!"}

SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'
access_token = "BQCfemif4Bjl-rgqyFrVg42AqWvWPX0MnbzRIWNlclfUqmqYvDDs7SXOVMTz-gITdT6UTjrSD-HOOnBn1F1Lig71R3TKIW74ciopJM3tpyOCxeOKdif9kHgfiII5xawV6T55XE9n0BFcXsKmKhfosmLO7_ImwcyZjYDY-JE7pFWrLCUVduxr2SwVvxLnVHzXszxd2JRLh2wACwDQUcgUpdWyu-sc"
refresh_token = None

CLIENT_ID = '36f15c5c0d4f424ea5c8f23193a87ef6'
CLIENT_SECRET = '04da3a43c83d4d8b8b2cce9f77398494'
redirect_uri = 'http://127.0.0.1:8000/callback'

def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

@app.get('/login')
def login():
    state = generate_random_string(16)
    scope = 'user-read-currently-playing'

    redirect_url = (
        'https://accounts.spotify.com/authorize?'
        f'response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={redirect_uri}&state={state}'
    )
    return RedirectResponse(redirect_url)

@app.get('/callback')
def callback(request: Request):
    global access_token
    global refresh_token

    code = request.query_params.get('code', None)
    state = request.query_params.get('state', None)

    if state is None:
        return RedirectResponse(f'/?error=state_mismatch')

    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        },
        'headers': {
            'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode(),
        }
    }
    response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        return {'access_token': access_token, 'refresh_token': refresh_token}

@app.get('/refresh_token')
def refresh_token():
    global access_token
    global refresh_token

    print(access_token)

    if refresh_token is None:
        return {'error': 'No refresh token available'}
    
    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    }

    response = requests.post(auth_options['url'], data=auth_options['data'])
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        print(access_token)
        return {'access_token': access_token}

# get current track 
def get_current_track():
    global access_token
    print(access_token)

    response = requests.get(
        SPOTIFY_GET_CURRENT_TRACK_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    json_resp = response.json()
    print(json_resp)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=json_resp.get('error'))

    track_id = json_resp['item']['id']
    track_name = json_resp['item']['name']
    artists = [artist for artist in json_resp['item']['artists']]

    link = json_resp['item']['external_urls']['spotify']

    artist_names = ', '.join([artist['name'] for artist in artists])

    current_track_info = {
        "id": track_id,
        "track_name": track_name,
        "artists": artist_names,
        "link": link
    }

    return current_track_info


@app.get("/currently-playing")
def currently_playing():
    try:
        current_track_info = get_current_track()
        return JSONResponse(content=current_track_info, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"error": str(e.detail)}, status_code=e.status_code)


def main():
    current_track_id = None
    while True:
        try:
            current_track_info = get_current_track(access_token)

            if current_track_info['id'] != current_track_id:
                print(current_track_info)
                current_track_id = current_track_info['id']

            time.sleep(3)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()

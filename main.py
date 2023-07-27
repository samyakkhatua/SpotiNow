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
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from deta import Deta
import asyncio

load_dotenv()

deta = Deta(os.getenv("DETA_PROJECT_KEY")) 
db = deta.Base("spotinowAuth")


app = FastAPI()

# Configure CORS
origins = [
    "https://links.samyakkhatua.in",
    "http://localhost:5173/",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():

    # db.put({"token": "Sam"})
    getAccessToken = db.get("r64qrgn7t9y0")
    # json_res = getAccessToken.json()
    accessToken = getAccessToken.get('accessToken')
    print(accessToken)
#     {
# 	"key": "r64qrgn7t9y0"
# 	"accessToken" : ""
# 	"refreshToken" : ""
# }

    return {"Welcome to Spotinow!"}

SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'
access_token = None
refresh_token = None
token_expires_at = None

# API credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")

redirect_uri = CALLBACK_URL

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
    global token_expires_at

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
        token_expires_at = time.time() + 3600  # Set default expiration time to 60 minutes (3600 seconds)
        return {'access_token': access_token, 'refresh_token': refresh_token}

def refresh_access_token():
    global access_token
    global token_expires_at

    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    }

    print("old: ",access_token[-10:])
    response = requests.post(auth_options['url'], data=auth_options['data'])
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        token_expires_at = time.time() + 3600  # Set default expiration time to 60 minutes (3600 seconds)
        print("new: ",access_token[-10:])
        return {'access_token': access_token}

def getAccessToken():
    global access_token

    access_token = db.get("r64qrgn7t9y0")
    return getAccessToken.get('accessToken')

async def get_current_track():
    global access_token

    print(access_token)
    await getAccessToken()
    print(access_token)

    response = requests.get(
        SPOTIFY_GET_CURRENT_TRACK_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    
    #if not playing
    if response.status_code == 204:
        return False
    
    
    print(response)
    json_resp = response.json()
    # print(json_resp)

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
    print( current_track_info)
    return current_track_info

@app.get("/currently-playing")
def currently_playing():
    
    try:
        current_track_info = get_current_track()
        if current_track_info==False:
            return False
        return current_track_info
    except HTTPException as e:
        return {"error": str(e.detail)}

@app.get("/refresh-token")
def refresh_token():
    try:
        refreshed_token = refresh_access_token()
        return refreshed_token
    except Exception as e:
        return {"error": str(e)}

def main():
    pass

if __name__ == '__main__':
    main()
    # getAccessToken()

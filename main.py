from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import requests
import time
from typing import Dict
from base64 import b64encode


app = FastAPI()

@app.get("/")
def read_root():
    return {"Welcome to Spotinow!"}

SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player/currently-playing'
ACCESS_TOKEN = 'BQDnIGCAiLFtN2Vmscih6ZQLMliVo2G3PvArApFzQvZ8CEWK-sFaxYjC5dY06AOgQkA_jSlNIoPOOf569qduRIEs4ElvTSkBQDHJ7yU2mqAT62XIcyQ'

CLIENT_ID = '36f15c5c0d4f424ea5c8f23193a87ef6'
CLIENT_SECRET = '04da3a43c83d4d8b8b2cce9f77398494'

# Get Token using client_credentials
# @app.on_event("startup")
@app.get("/token")
def get_access_token():
    global ACCESS_TOKEN
    credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}"}
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    ACCESS_TOKEN = response.json()["access_token"]
    print(response.json())
    print(ACCESS_TOKEN)
    # return ACCESS_TOKEN

# get current track 
def get_current_track(access_token: str) -> Dict[str, str]:
    print(access_token)
    response = requests.get(
        SPOTIFY_GET_CURRENT_TRACK_URL,
        headers={
            "Authorization":access_token
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
        print(ACCESS_TOKEN)
        current_track_info = get_current_track(ACCESS_TOKEN)
        return JSONResponse(content=current_track_info, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"error": str(e.detail)}, status_code=e.status_code)


def main():
    current_track_id = None
    while True:
        try:
            current_track_info = get_current_track(ACCESS_TOKEN)

            if current_track_info['id'] != current_track_id:
                print(current_track_info)
                current_track_id = current_track_info['id']

            time.sleep(3)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()

# SpotiNow
## Seamless integration with your Spotify account, allowing you to effortlessly showcase the currently playing song in real-time.

Spotinow is a web application that allows you to authenticate with Spotify, retrieve and display the currently playing track, and refresh the access token when needed. The app is built using FastAPI, a modern, fast, web framework for building APIs with Python. It utilizes OAuth2.0 for Spotify authentication and communicates with the Spotify Web API to fetch and display the current track information.


### FrontEnd Showcase Link : https://links.samyakkhatua.in
### Backend Deployed Link : https://spotinow-1-t1281143.deta.app
### Guthub Repo : https://github.com/samyakkhatua/spotinow 

## Demo

![Coming Soon](XK99IqSdSMjbmP4Mn/giphy.)


## Features

- User authentication with Spotify
- Retrieval of the currently playing track from Spotify
- Automatic access token refreshing
- CORS configuration to allow specific origins


## Tech Stack

- FastAPI: Web framework used for building the API
- Python: The programming language used for server-side logic
- Requests: Library for making HTTP requests to the Spotify API
- FastAPI Middleware: For enabling Cross-Origin Resource Sharing (CORS)
- Deta: For deploying the FastAPI Backend


## Run Locally

Clone the project

```bash
  git clone https://github.com/samyakkhatua/spotinow.git

```

Go to the project directory
```bash
  cd spotinow

```

Install dependencies

```bash
  pip install -r requirements.txt

```


Create a .env file in the project root and set the following environment variables:
```bash
CLIENT_ID = <Your-Spotify-Client-ID>
CLIENT_SECRET = <Your-Spotify-Client-Secret>
CALLBACK_URL = <Your-Callback-URL>
```
Replace <Your-Spotify-Client-ID>, <Your-Spotify-Client-Secret>, and <Your-Callback-URL> with your actual Spotify application credentials.

Run the FastAPI application:
```bash
  uvicorn main:app --reload

```




## API Reference

#### Authorize

```http
  GET /login
```

| Response | Type     | Description                |
| :-------- | :------- | :------------------------- |
| Redirects the user to the Spotify authorization page. |  | Initiates the Spotify authentication flow. |

#### Get currently playing Song

```http
  GET /currently-playing
```

| Response | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| JSON with track information or false if no track is currently playing      | JSON | Retrieves the currently playing track information from Spotify |


#### Access Token refresh

```http
  GET /refresh-token
```

| Response | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| JSON with the refreshed access token | JSON | Refreshes the access token using the refresh token. |



## Feedback

If you have any feedback, please reach out to us at hello@samyakkhatua.in


## Authors

- [@samyakkhatua](https://www.github.com/samyakkhatua)

## Roadmap

Currently, Spotinow provides basic functionality for fetching the currently playing track from Spotify. Future enhancements may include:

- Support for handling playback controls (play, pause, skip, etc.).
- Playlist management (create, update, delete playlists).
- Enhanced error handling and user feedback.
- Support for more Spotify API endpoints.


I welcome contributions from the community to improve and expand Spotinow further. If you find any issues or have ideas for improvements, please feel free to contribute by creating pull requests.
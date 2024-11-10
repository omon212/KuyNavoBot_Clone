import requests

url = "https://spotify-downloader9.p.rapidapi.com/downloadSong"

querystring = {"songId":"https://open.spotify.com/track/7jT3LcNj4XPYOlbNkPWNhU"}

headers = {
	"x-rapidapi-key": "4e3f34f7femsh7a9d112e3fee647p125284jsn050cb0333c97",
	"x-rapidapi-host": "spotify-downloader9.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
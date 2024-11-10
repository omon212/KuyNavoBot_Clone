import httpx

async def download_tiktok(url):
    api_url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    payload = {"url": url}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "0f95c9454bmshfbfff6f7be74315p12102djsnc98492887d39",
        "X-RapidAPI-Host": "auto-download-all-in-one.p.rapidapi.com"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=payload, headers=headers)
        return response.json()
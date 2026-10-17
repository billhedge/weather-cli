import requests
import requests_cache

GEOCODE_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"

requests_cache.install_cache("weathercli_cache", expire_after=3600)

geocode_response = requests.get(GEOCODE_ENDPOINT, params={"name": input("Enter a location: ")})
geocode_response.raise_for_status()
print(geocode_response.json())


from hubs.models import Hub
import requests


def geocode_location(location):
        # Implement geocoding logic here and return coordinates
        # Example code:
        access_token = "pk.eyJ1IjoibmloYWxyb3NoYW4iLCJhIjoiY2xsZGIyNW5wMGFxMjN1cXkwZm5reHlrdSJ9.l2JGuFbgbkgYWJl4vDOUig"
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={access_token}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if len(data['features']) > 0:
                    coordinates = data['features'][0]['center']
                    return coordinates
        except requests.exceptions.RequestException:
            return None



def find_nearby_hubs(coordinates):
    hubs = Hub.objects.all()
    nearby_hubs = []

    # Define the maximum distance in meters for a hub to be considered "nearby"
    max_distance_meters = 50000

    access_token = "pk.eyJ1IjoibmloYWxyb3NoYW4iLCJhIjoiY2xsZGIyNW5wMGFxMjN1cXkwZm5reHlrdSJ9.l2JGuFbgbkgYWJl4vDOUig"
    distance_api_url = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coordinates}"
    params = {
        "access_token": access_token,
    }

    for hub in hubs:
        coordinates_str = f"{coordinates[0]},{coordinates[1]};{hub.location.x},{hub.location.y}"
        distance_api_url_formatted = distance_api_url.format(coordinates=coordinates_str)

        try:
            response = requests.get(distance_api_url_formatted, params=params)
            if response.status_code == 200:
                data = response.json()
                if "routes" in data and data["routes"]:
                    distance_to_hub_meters = data["routes"][0]["distance"]
                    distance_to_hub_kilometers = distance_to_hub_meters / 1000  # Convert to kilometers
                    if distance_to_hub_kilometers < (max_distance_meters / 1000):
                        nearby_hubs.append({
                            "hub_name": hub.hub_name,
                            "distance_km": distance_to_hub_kilometers,
                            "hub_location_x": hub.location.x,
                            "hub_location_y": hub.location.y,
                            "hub": hub,
                        })
        except requests.exceptions.RequestException as e:
            raise ValidationError({"message": f"Error calculating distance to hubs: {str(e)}"})

    # Sort 'nearby_hubs' by distance (optional)
    nearby_hubs.sort(key=lambda x: x["distance_km"])
    return nearby_hubs

def calculate_distance(coordinat1,coordinat2):
    access_token = "pk.eyJ1IjoibmloYWxyb3NoYW4iLCJhIjoiY2xsZGIyNW5wMGFxMjN1cXkwZm5reHlrdSJ9.l2JGuFbgbkgYWJl4vDOUig"
    distance_api_url = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coordinates}"
    params = {
        "access_token": access_token,
    }
    coordinates_str = f"{coordinat1[0]},{coordinat1[1]};{coordinat2[0]},{coordinat2[1]}"
    distance_api_url = distance_api_url.format(coordinates=coordinates_str)
    response = requests.get(distance_api_url, params=params)
    try:
        # response = requests.get(directions_url)
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and data["routes"]:
                return data["routes"][0]["distance"]
    except:
        pass
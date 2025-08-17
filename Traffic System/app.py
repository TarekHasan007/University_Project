import folium
import requests
from geopy.geocoders import Nominatim
import polyline
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Function to get coordinates from an address
def get_coordinates(address):
    geolocator = Nominatim(user_agent="myApp")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Function to get route from OSRM API
def get_route(start_lat, start_lon, end_lat, end_lon):
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=polyline"
    response = requests.get(osrm_url)
    route_data = response.json()
    
    if route_data.get("routes"):
        distance = route_data['routes'][0]['legs'][0]['distance'] / 1000  # meters to km
        duration = route_data['routes'][0]['legs'][0]['duration'] / 60  # seconds to minutes
        route_polyline = route_data['routes'][0]['geometry']
        route_coordinates = polyline.decode(route_polyline)
        return distance, duration, route_coordinates
    else:
        return None, None, None


def format_time(minutes):
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    return f"{hours}h:{remaining_minutes}m"

def calculate_time(distance, speed_kmh):
    time_minutes = (distance / speed_kmh) * 60  # Convert hours to minutes
    return time_minutes


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get input from user
        start_address = request.form["start"]
        end_address = request.form["end"]

        # Get coordinates for the start and end locations
        start_lat, start_lon = get_coordinates(start_address)
        end_lat, end_lon = get_coordinates(end_address)

        if start_lat is not None and end_lat is not None:
            # Get route details
            distance, duration, route_coordinates = get_route(start_lat, start_lon, end_lat, end_lon)

            # Travel modes (car and bike)
            car_speed = 60  # km/h
            bike_speed = 30  # km/h

            # Calculate travel time for different modes
            time_by_car = calculate_time(distance, car_speed)
            time_by_bike = calculate_time(distance, bike_speed)

            # Format times
            time_by_car_formatted = format_time(time_by_car)
            time_by_bike_formatted = format_time(time_by_bike)


            # Check if route data was successfully retrieved
            if route_coordinates:
                # Generate the map
                map = folium.Map(location=[start_lat, start_lon], zoom_start=13)
                folium.Marker([start_lat, start_lon], popup="Start").add_to(map)
                folium.Marker([end_lat, end_lon], popup="End").add_to(map)
                folium.PolyLine(route_coordinates, color="blue", weight=5, opacity=0.7).add_to(map)



                # Add distance and duration as an HTML overlay on top of the map
                distance_time_html = f"""
                <div style="position: fixed; top: 100px; left: 30px; 
                        background-color: white; padding: 10px; 
                        border: 2px solid black; z-index: 1000;">
                    <h4>Route Details:</h4>
                    <p><b>Distance:</b> {distance:.2f} km</p>
                    <p><b>By Car:</b> {time_by_car_formatted}</p>
                    <p><b>By Bike:</b> {time_by_bike_formatted}</p>
                </div>
                """
                # Add an empty info box for route details
                info_box_html = """
                <div id="info-box" style="position: fixed; top: 10px; left: 30px; 
                        background-color: white; padding: 10px; 
                        border: 2px solid black; z-index: 1000;">
                    <h4>Route Details:</h4>
                    <p>Click on the map to set the start and end points.</p>
                </div>
                """
                map.get_root().html.add_child(folium.Element(info_box_html))

                # Add HTML overlay to the map
                map.get_root().html.add_child(folium.Element(distance_time_html))

                # Save the map
                map.save("templates/map.html")
                print(f"Distance: {distance:.2f} km")
                print(f"Duration: {duration:.2f} minutes")

                return render_template("map.html", distance=distance, duration=duration)
            else:
                return render_template("index.html", error="Unable to fetch route data. Please try again.")
        else:
            return render_template("index.html", error="Invalid addresses. Please try again.")
    return render_template("index.html")




    # Calculate route
    distance, duration, route_coordinates = get_route(start_lat, start_lon, end_lat, end_lon)
    
    return jsonify({
        'distance': distance,
        'duration': duration,
        'route_coordinates': route_coordinates
    })

if __name__ == "__main__":
    app.run(debug=True)


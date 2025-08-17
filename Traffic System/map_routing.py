import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_coordinates(location_name):
    """
    Get the latitude and longitude for a given location name using geopy.
    """
    geolocator = Nominatim(user_agent="map_routing_app")
    
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"Location '{location_name}' not found.")
            return None
    except GeocoderTimedOut:
        print("Geocoding service timed out. Please try again.")
        return None

def calculate_distance(start, end):
    """
    Calculate the Haversine distance between two points on the Earth's surface.
    The points are given as (latitude, longitude).
    """
    # Using geopy's geodesic method to calculate distance
    from geopy.distance import geodesic
    distance = geodesic(start, end).km
    return distance

def calculate_time(distance, speed_kmh=60):
    """
    Calculate time to travel the distance at a given speed (default 60 km/h).
    """
    time = distance / speed_kmh  # Time = Distance / Speed
    return time

def get_location_input(location_name):
    """
    Ask the user for the name of a location and return its coordinates.
    """
    while True:
        location_name = input(f"Enter the name of {location_name}: ")
        coordinates = get_coordinates(location_name)
        if coordinates:
            return coordinates
        else:
            print("Invalid location name. Please try again.")

def main():
    print("Welcome to the Map Routing System")
    
    # Get user input for start and end locations by name
    start_location = get_location_input("Start Location")
    end_location = get_location_input("End Location")
    
    # Calculate the distance between the start and end points
    distance = calculate_distance(start_location, end_location)
    
    # Calculate the estimated time to travel at 60 km/h
    time = calculate_time(distance)
    
    # Output the results
    print(f"\nRoute Details:")
    print(f"Start Location: {start_location}")
    print(f"End Location: {end_location}")
    print(f"Distance: {distance:.2f} km")
    print(f"Estimated Time to Travel: {time:.2f} hours")

if __name__ == "__main__":
    main()

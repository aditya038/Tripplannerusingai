import os
import google.generativeai as genai
import googlemaps
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Set API Keys
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key is not set. Please set the GEMINI_API_KEY environment variable.")

# Configure Gemini API
genai.configure(api_key=api_key)

# Initialize the Google Maps API client
gmaps = googlemaps.Client(key="MAPS_API_KEY")

# Create the Gemini model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(model_name='gemini-1.5-flash')
response = model.generate_content(
    ['Do these look store-bought or homemade?'],
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }
)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "You are a chatbot for a travel planner website named TripDarzee, and your name is 'TravelMitra.' "
        "Your primary role is to assist users in planning their trips by gathering their preferences, such as "
        "destination, travel dates, and budget. You will generate personalized itineraries based on user inputs and "
        "provide recommendations for accommodations, transportation, and local attractions. You should also offer "
        "real-time updates on weather, local events, and travel advisories. Ensure that your responses are helpful, "
        "accurate, and tailored to individual user needs, and be ready to handle modifications to trip plans as "
        "requested by the users."
    ),
)

history = []

print("Bot: Hello there! 👋 Welcome to TripDarzee! I'm TravelMitra, your personal travel assistant. "
      "What kind of trip are you dreaming of? Tell me all about it, and I'll help you weave a perfect travel tapestry! 🧵✨")

def find_nearby_places(location, place_type='hotel', radius=2000):
    """
    Find nearby places using Google Maps API.
    :param location: The location to search around (e.g., "Paris").
    :param place_type: Type of place to search for (e.g., 'hotel', 'restaurant').
    :param radius: Search radius in meters.
    :return: A list of nearby places.
    """
    # Geocode the location to get latitude and longitude
    geocode_result = gmaps.geocode(location)
    if not geocode_result:
        return f"Sorry, I couldn't find the location: {location}."
    
    # Get the coordinates
    coordinates = geocode_result[0]['geometry']['location']
    lat = coordinates['lat']
    lng = coordinates['lng']
    
    # Perform a nearby search
    places_result = gmaps.places_nearby(location=(lat, lng), radius=radius, type=place_type)

    if places_result['status'] == 'OK':
        # Extract the names of the nearby places
        places = [place['name'] for place in places_result['results']]
        return f"Here are some {place_type}s near {location}: " + ', '.join(places)
    else:
        return f"Sorry, I couldn't find any {place_type}s near {location}."


# Main chatbot loop
while True:
    user_input = input("You: ")
    
    # Check if the user is requesting nearby places (e.g., "Find hotels near Paris")
    if "find" in user_input.lower() and "near" in user_input.lower():
        # Example: "Find hotels near Paris"
        words = user_input.split()
        place_type = words[1]  # assuming the second word is the type of place (e.g., 'hotel', 'restaurant')
        location = ' '.join(words[3:])  # assuming the location comes after 'near'
        
        # Find nearby places using the Google Maps API
        places_response = find_nearby_places(location, place_type=place_type)
        print(f"Bot: {places_response}")
    
    else:
        # Regular chatbot flow using Gemini API
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_input)
        
        model_response = response.text
        print(f"Bot: {model_response}")
        
        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [model_response]})

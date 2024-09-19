import os
import requests
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Set API Keys
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key is not set. Please set the GEMINI_API_KEY environment variable.")
mapquest_api_key = os.getenv("MAPS_API_KEY")  # Replace with your MapQuest API Key

# Configure Gemini API
genai.configure(api_key=api_key)

# Create the Gemini model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

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

def geocode_location(location):
    url = "http://www.mapquestapi.com/geocoding/v1/address"
    params = {
        "key": mapquest_api_key,
        "location": location
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200 and data['info']['statuscode'] == 0:
        location = data['results'][0]['locations'][0]['latLng']
        return location['lat'], location['lng']
    else:
        return None, None

def find_nearby_places(lat, lng, place_type='hotel', radius=2000):
    url = "http://www.mapquestapi.com/search/v4/place"
    params = {
        "key": mapquest_api_key,
        "location": f"{lat},{lng}",
        "sort": "distance",
        "feedback": False,
        "q": place_type,
        "circle": f"{lng},{lat},{radius}"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200 and "results" in data:
        places = [result["name"] for result in data["results"]]
        return f"Here are some {place_type}s nearby: " + ", ".join(places)
    else:
        return f"Sorry, I couldn't find any {place_type}s near the given location."

while True:
    user_input = input("You: ")
    
    if "find" in user_input.lower() and "near" in user_input.lower():
        words = user_input.split()
        place_type = words[1]
        location = ' '.join(words[3:])
        
        lat, lng = geocode_location(location)
        
        if lat and lng:
            places_response = find_nearby_places(lat, lng, place_type=place_type)
            print(f"Bot: {places_response}")
        else:
            print(f"Bot: Sorry, I couldn't find the location: {location}.")
    
    else:
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_input)
        
        model_response = response.text
        print(f"Bot: {model_response}")
        
        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [model_response]})

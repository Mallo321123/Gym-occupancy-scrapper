import requests
import time
from datetime import datetime
import threading
import paho.mqtt.client as mqtt

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.content.decode('utf-8')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("mqtt-broker.fritz.box", 1883, 60)

def mqtt_thread():
    client.loop_forever()
    
threading.Thread(target=mqtt_thread, daemon=True).start()

if __name__ == "__main__":
    while True:
        url = "https://easyfitness.club/studio/easyfitness-regensburg"
        data = fetch_data(url)

        if not data:
            raise Exception("Failed to fetch data from the URL.")

        relevant_container = data.split(
            '<div class="magicline-auslastung auslastung show-on-mobile">'
        )[1].split("</div>")[0]
        
        print(relevant_container)
        
        try:
            percent = int(relevant_container.split('class="meterbubble">')[1].split("</span>")[0].strip("%"))
            
        except (IndexError, ValueError) as e:
            raise Exception("Failed to parse the occupancy percentage.") from e
        
        try:
            last_update = relevant_container.split('Zuletzt aktualisiert: ')[1].split("</div>")[0].strip(" Uhr")
            
        except (IndexError, ValueError) as e:
            raise Exception("Failed to parse the last update time.") from e

        print(f"percent: {percent}, last update: {last_update}")
        
        data = {"percent": percent, "last_update": last_update}
        
        client.publish("fitness", str(data))
        
        time.sleep(120)  # Wait for 2 minutes before the next fetch
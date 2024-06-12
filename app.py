from flask import Flask, request, jsonify
import requests
from config import API_KEYS
from flask_cors import CORS
from flask_mail import Mail
from flask_mail import Message
import logging
import numpy as np
import joblib 


app = Flask(__name__)
CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tefymaherison19@gmail.com'
app.config['MAIL_PASSWORD'] = 'hxwf kpua wjfx pwdh'

mail = Mail(app)

cities = ["Paris", "New York", "Tokyo", "London","Lyon","Beijing", "Moscow", "Sydney", "Toronto", "Dubai", 
    "Berlin", "Rome", "Istanbul", "Madrid", "Buenos Aires",
    "Mumbai", "Cairo", "Bangkok", "Mexico City", "Seoul",
    "Lagos", "Jakarta", "São Paulo", "Los Angeles", "Chicago",
    "Hong Kong", "Kuala Lumpur", "Lima", "Shanghai", "Cape Town"]

# Route pour récupérer les données météorologiques par ville
@app.route('/weather/city', methods=['GET'])

def get_all_weather():
    # Votre clé d'API WeatherAPI
    # api_key = 'bc51670c71df489d91374131241605'
    
    # Dictionnaire pour stocker les données météorologiques de toutes les cities
    all_weather_data = {}
    
    # Parcourir la liste de cities et récupérer les données météorologiques pour chaque ville
    for city in cities:
        # URL de l'API WeatherAPI pour obtenir les données météorologiques de la ville actuelle
        url = f'http://api.weatherapi.com/v1/current.json?key={API_KEYS}&q={city}'
          
        # Envoyer une requête GET à l'API WeatherAPI
        response = requests.get(url)
        
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Convertir la réponse JSON en dictionnaire Python
            data = response.json()
            
            # Extraire les informations météorologiques pertinentes
            weather_data = {
                'city': data['location']['name'],
                'temperature': data['current']['temp_c'],
                'condition': data['current']['condition']['text'],
                'région' : data['location']['region']
                # Ajoutez d'autres données météorologiques pertinentes si nécessaire
            }
            
            # Ajouter les données météorologiques de la ville au dictionnaire global
            all_weather_data[city] = weather_data
    
    # Retourner toutes les données météorologiques au format JSON
    return jsonify(all_weather_data)



# Route pour la lcoalisation de l'utilisateur et renvoie la météo
@app.route('/weather/userlocation' ,methods=['GET'] )

def get_current_location_weather():
    # Obtenez les coordonnées de localisation de l'utilisateur à partir de la requête
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    print(longitude,latitude)

    # Votre clé d'API WeatherAPI
   
    
    # URL de l'API WeatherAPI pour obtenir les données météorologiques actuelles en fonction des coordonnées
    url = f'http://api.weatherapi.com/v1/current.json?key={API_KEYS}&q={latitude},{longitude}'
    
    # Envoyer une requête GET à l'API WeatherAPI
    response = requests.get(url)
    
    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Convertir la réponse JSON en dictionnaire Python
        data = response.json()
        
        # Extraire les informations météorologiques pertinentes
        current_location_weather_data = {
            'city': data['location']['name'],
            'temperature': data['current']['temp_c'],
            'condition': data['current']['condition']['text'],
            'région' : data['location']['region']
            # Ajoutez d'autres données météorologiques pertinentes si nécessaire
        }
        
        return jsonify(current_location_weather_data)
    else:
        # En cas d'échec de la requête, renvoyer un message d'erreur
        return jsonify({'error': 'Failed to fetch weather data'}), 500




# R oute pour les historiques 
@app.route('/weather/historical', methods=['GET'])
def get_historical_weather():
    # Obtenez le nom de la ville spécifiée à partir de la requête
    city = request.args.get('city')

    # Votre clé d'API WeatherAPI
    
    # Date de début et de fin pour la période historique (par exemple, les 7 derniers jours)
    import datetime
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)  # Obtenez les données des 7 derniers jours
    
    # URL de l'API WeatherAPI pour obtenir les données météorologiques historiques pour une ville spécifiée
    url = f'http://api.weatherapi.com/v1/history.json?key={API_KEYS}&q={city}&dt={start_date}&end_dt={end_date}'
    
    # Envoyer une requête GET à l'API WeatherAPI
    response = requests.get(url)
    
    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Convertir la réponse JSON en dictionnaire Python
        data = response.json()
        
        # Extraire les informations météorologiques pertinentes
        historical_weather_data = {
        
        'date': data['forecast']['forecastday'][0]['date'],
        'avgtemp_c': data['forecast']['forecastday'][0]['day']['avgtemp_c'],
        'maxtemp_c': data['forecast']['forecastday'][0]['day']['maxtemp_c'],
        'mintemp_c': data['forecast']['forecastday'][0]['day']['mintemp_c'],
        'humidity': data['forecast']['forecastday'][0]['day']['avghumidity'],
        'precip_mm': data['forecast']['forecastday'][0]['day']['totalprecip_mm']
            # Ajoutez d'autres données météorologiques pertinentes si nécessaire
        }
        
        return jsonify(historical_weather_data)
    else:
        # En cas d'échec de la requête, renvoyer un message d'erreur
        return jsonify({'error': 'Failed to fetch historical weather data'}), 500



#Route pour envoyer les emails 
@app.route('/sendmail', methods=['POST'])
def send_email():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message_content = data.get('message')

    msg = Message(
        subject="Bug Report",
        sender=email,
        recipients=["tefymaherison19@gmail.com"],  # Remplacez par l'email du développeur
        body=f"Nom: {name}\nEmail: {email}\n\nMessage:\n{message_content}"
    )
    msg.add_recipient(email)

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully!"}), 200
    except Exception as e:
        logging.error("Error sending email", exc_info=True)
        return jsonify({"error": str(e)}), 500


# Charger le modèle et le scaler
model = joblib.load('weather_model.pkl')
scaler = joblib.load('scaler.pkl')
#route prédiction 
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_data = np.array([data['maxtemp_c'], data['mintemp_c'], data['avgtemp_c'], data['maxwind_kph'], data['totalprecip_mm'], data['avgvis_km'], data['avghumidity']]).reshape(1, -1)
    input_data = scaler.transform(input_data)
    prediction = model.predict(input_data)
    return jsonify({'predicted_maxtemp_c': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)


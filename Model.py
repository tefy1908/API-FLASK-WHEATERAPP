import requests
import pandas as pd
from config import API_KEYS
import joblib
from datetime import datetime, timedelta


LOCATION = 'Paris'
HISTORY_ENDPOINT = f'https://api.weatherapi.com/v1/history.json?key=bc51670c71df489d91374131241605&q=London&dt='

# Fonction pour récupérer les données historiques
def fetch_weather_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    date_range = pd.date_range(start=start_date, end=end_date)
    weather_data = []

    for date in date_range:
        # print(HISTORY_ENDPOINT + date.strftime('%Y-%m-%d'))
        #on utilise 7 jours car l'api nous permet que de récupérer les 7 derneirs jorus d'historique 
        response = requests.get(HISTORY_ENDPOINT + date.strftime('%Y-%m-%d'))
        if response.status_code == 200:
            data = response.json()
            weather_data.append(data['forecast']['forecastday'][0])
            weather_data.append(data['forecast']['forecastday'][0]['day'])
        else:
            print(f"Failed to fetch data for {date.strftime('%Y-%m-%d')}: {response.json()}")

    return pd.DataFrame(weather_data)

# Exemple de récupération de données pour une période donnée
# Exemple de récupération de données pour une période donnée
weather_data = fetch_weather_data()
weather_data.to_csv('historical_weather_data.csv', index=False)

# Charger les données
weather_data = pd.read_csv('historical_weather_data.csv')

# # Prétraitement
weather_data['date'] = pd.to_datetime(weather_data['date'])
weather_data.set_index('date', inplace=True)


weather_data = weather_data.dropna()
# # Sélection des caractéristiques et de la cible
features = weather_data['maxtemp_c', 'mintemp_c', 'avgtemp_c', 'maxwind_kph', 'totalprecip_mm', 'avgvis_km', 'avghumidity']
target = weather_data['maxtemp_c']

# # Normalisation des caractéristiques
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(features)


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# # Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(scaled_features, target, test_size=0.2, random_state=42)

# # Entraînement du modèle
model = LinearRegression()
model.fit(X_train, y_train)

# # Évaluation du modèle
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f'Mean Squared Error: {mse}')


# # Sauvegarde du modèle et du scaler
# joblib.dump(model, 'weather_model.pkl')
# joblib.dump(scaler, 'scaler.pkl')
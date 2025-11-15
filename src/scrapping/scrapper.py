
import requests 
import os
from dotenv import load_dotenv 
import sys 

load_dotenv()

api_key = os.getenv("JAMENDO_API_KEY")
    
base_url = r"https://api.jamendo.com/v3.0"

endpoint = f"/tracks/?client_id={api_key}&limit=100"

endpoint = "/tracks/"

params = {
    'client_id': api_key,
    'format': 'json',
    'limit': 50,
    'tags':"relaxation+ambient+easylistening",
    'vocalinstrumental': 'instrumental'
}

response = requests.get(base_url + endpoint, params=params)

if response.status_code == 200:
    data = response.json()

    if 'headers' in data and 'warnings' in data['headers']:
        print(f"Advertencia de la API: {data['headers']['warnings']}")

    tracks = data.get('results', [])

    for track in tracks:
        print(f"Nombre de la canción: {track['name']}")
        print(f"Artista: {track['artist_name']}")
        print(f"Enlace a la pista: {track['audio']}")

        print() 
else:
    print("Error al hacer la solicitud:", response.status_code)

download_folder = 'jamendo_tracks'
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

print(f"Descargando {len(tracks)} pistas...")

for track in tracks:
    track_name = track.get('name', 'unknown_track').replace('/', '_').replace('\\', '_')
    artist_name = track.get('artist_name', 'unknown_artist').replace('/', '_').replace('\\', '_')
    audio_url = track.get('audio')

    if audio_url:
        file_name = f"{track_name} - {artist_name}.mp3"
        file_path = os.path.join(download_folder, file_name)
        print(f"Descargando: {file_name}")
        try:
            audio_response = requests.get(audio_url, stream=True)
            if audio_response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Guardado: {file_path}")
            else:
                print(f"Error al descargar {file_name}: {audio_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al descargar {file_name}: {e}")
    else:
        print(f"URL de audio no encontrada para la pista: {track_name}")

print("Descarga completada.")
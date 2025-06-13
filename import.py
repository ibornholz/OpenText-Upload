import requests
import os

# Eingabe: Personalnummer und Dateiname
persnr = '12345'  # ← gewünschte Personalnummer
local_file_name = 'test.pdf'

# Basis-URLs
BASE_URL = 'PATH TO OT /cs/cs/api/v1'
API_ROOT = BASE_URL.replace('/api/v1', '')  # z.B. https://.../cs/cs

# Benutzeranmeldeinformationen
username = 'UNAME'
password = 'PASS'

# 1. Authentifizierung
auth_url = f'{BASE_URL}/auth'
auth_data = {'username': username, 'password': password}
auth_response = requests.post(auth_url, data=auth_data)
auth_response.raise_for_status()
otcsticket = auth_response.json().get('ticket')
if not otcsticket:
    raise Exception('Authentifizierung fehlgeschlagen.')

# 2. Suche nach Business Workspace (v2)
search_url = (
    f"{API_ROOT}/api/v2/businessworkspaces"
    f"?where_name=contains_{persnr}"
)
headers = {'otcsticket': otcsticket}  # <-- Hier angepasst

# LOGGING: API-Call anzeigen
print("\n Suche Business Workspace")
print("  URL:", search_url)
print("  Header:", {k: (v[:10] + '...') if k == 'otcsticket' else v for k, v in headers.items()})

# 3. Request ausführen
search_response = requests.get(search_url, headers=headers)
print(" Status:", search_response.status_code)
print(" Antwort-Auszug:", search_response.json().get("data", [])[:1])  # Nur erster Treffer

search_response.raise_for_status()

# 4. Extrahiere parent_id aus results statt data
response_json = search_response.json()
results = response_json.get('results', [])

if not results:
    raise Exception(f'Keine Akte gefunden für Personalnummer: {persnr}')

first_result = results[0]
parent_id = first_result.get('data', {}).get('properties', {}).get('id')
if not parent_id:
    raise Exception('Keine Node-ID gefunden im Ergebnis.')

print(f" Gefundene Akte mit Node-ID: {parent_id}")


# 5. Datei laden
file_path = os.path.join(os.getcwd(), local_file_name)
if not os.path.isfile(file_path):
    raise FileNotFoundError(f'Datei nicht gefunden: {file_path}')
with open(file_path, 'rb') as f:
    file_content = f.read()

# 6. Datei-Upload
upload_url = f'{BASE_URL}/nodes'
upload_headers = {'otcsticket': otcsticket}
files = {
    'type': (None, '144'),
    'parent_id': (None, str(parent_id)),
    'name': (None, local_file_name),
    'file': (local_file_name, file_content, 'application/pdf')
}
upload_response = requests.post(upload_url, headers=upload_headers, files=files)
upload_response.raise_for_status()

print('\n PDF erfolgreich hochgeladen:', upload_response.json())

from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# OAuth Configuration
TOKEN_URL = "https://identity.primaverabss.com/connect/token"
CLIENT_ID = "APP-KEY"
CLIENT_SECRET = "aad917fb-bfdb-46a0-906c-f55a58dbb3e3"
SCOPE = "application"

# API Configuration
BASE_URL = "https://my.jasminsoftware.com"
TENANT = "329459"
ORGANIZATION = "329459-0001"
ENDPOINT_ODATA = f"{BASE_URL}/api/{TENANT}/{ORGANIZATION}/salesCore/customerParties/odata"
ENDPOINT_PARTY_KEY = f"{BASE_URL}/api/{TENANT}/{ORGANIZATION}/salesCore/customerParties"

# Global Token Variables
ACCESS_TOKEN = None
TOKEN_EXPIRATION = 0

# Function to Get or Refresh Access Token
def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRATION
    if ACCESS_TOKEN and time.time() < TOKEN_EXPIRATION:
        return ACCESS_TOKEN

    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": SCOPE,
            },
        )
        if response.status_code == 200:
            token_data = response.json()
            ACCESS_TOKEN = token_data["access_token"]
            TOKEN_EXPIRATION = time.time() + token_data["expires_in"] - 60  # Add buffer
            return ACCESS_TOKEN
        else:
            raise Exception(f"Failed to fetch token: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred while fetching the token: {e}")

# Route to Fetch All Party Keys
@app.route('/fetch_party_keys', methods=['GET'])
def fetch_all_party_keys():
    try:
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.get(ENDPOINT_ODATA, headers=headers)
        if response.status_code == 200:
            data = response.json()
            party_keys = [item.get("partyKey") for item in data.get("items", []) if "partyKey" in item]
            return jsonify({"partyKeys": party_keys})
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to Fetch Data for a Specific Party Key
@app.route('/fetch_party_data/<party_key>', methods=['GET'])
def fetch_data_for_party_key(party_key):
    try:
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        specific_url = f"{ENDPOINT_PARTY_KEY}/{party_key}"
        response = requests.get(specific_url, headers=headers)
        if response.status_code == 200:
            full_data = response.json()
            limited_data = {
                "_id": full_data.get("partyKey"),
                "Name": full_data.get("name"),
                "Email": full_data.get("email"),
                "Mobile": full_data.get("mobile"),
                "CompanyTaxID": full_data.get("companyTaxID"),
                "StreetName": full_data.get("streetName"),
                "PostalZone": full_data.get("postalZone"),
                "CityName": full_data.get("cityName"),
                "Country": full_data.get("country"),
            }
            return jsonify(limited_data)
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

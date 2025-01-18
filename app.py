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

ENDPOINT_ODATA_PRODUCTS = f"{BASE_URL}/api/{TENANT}/{ORGANIZATION}/salesCore/salesItems/extension/odata"
ENDPOINT_ITEM_KEY = f"{BASE_URL}/api/{TENANT}/{ORGANIZATION}/salesCore/salesItems"

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

#########################################################################################################
#########################################################################################################

# Route to Fetch All Data (products) Automatically
@app.route('/fetch_all_products', methods=['GET'])
def fetch_all_data():
    try:
        # Get the access token
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Step 1: Fetch all item keys
        response = requests.get(ENDPOINT_ODATA_PRODUCTS, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code

        data = response.json()
        item_keys = [item.get("itemKey") for item in data.get("items", []) if "itemKey" in item]

        # Step 2: Fetch data for each item key
        all_data = []
        for item_key in item_keys:
            specific_url = f"{ENDPOINT_ITEM_KEY}/{item_key}"
            item_response = requests.get(specific_url, headers=headers)
            if item_response.status_code == 200:
                full_data = item_response.json()
                limited_data = {
                    "ID": full_data.get("itemKey"),
                    "Description": full_data.get("description"),
                    "Image": full_data.get("image"),
                    "ImageThumbnail": full_data.get("imageThumbnail"),
                    "Brand": full_data.get("brand"),
                    "BrandModel": full_data.get("brandModel")
                }
                all_data.append(limited_data)

        return jsonify(all_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#########################################################################################################
#########################################################################################################

# Route to Fetch All Data (products) Automatically
@app.route('/fetch_all_data', methods=['GET'])
def fetch_all_data():
    try:
        # Get the access token
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Step 1: Fetch all party keys
        response = requests.get(ENDPOINT_ODATA, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code

        data = response.json()
        party_keys = [item.get("partyKey") for item in data.get("items", []) if "partyKey" in item]

        # Step 2: Fetch data for each party key
        all_data = []
        for party_key in party_keys:
            specific_url = f"{ENDPOINT_PARTY_KEY}/{party_key}"
            party_response = requests.get(specific_url, headers=headers)
            if party_response.status_code == 200:
                full_data = party_response.json()
                limited_data = {
                    "ID": full_data.get("partyKey"),
                    "Name": full_data.get("name"),
                    "Email": full_data.get("electronicMail"),
                    "Mobile": full_data.get("mobile"),
                    "CompanyTaxID": full_data.get("companyTaxID"),
                    "StreetName": full_data.get("streetName"),
                    "PostalZone": full_data.get("postalZone"),
                    "CityName": full_data.get("cityName"),
                    "Country": full_data.get("country"),
                }
                all_data.append(limited_data)

        return jsonify(all_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#########################################################################################################
#########################################################################################################

if __name__ == '__main__':
    app.run(debug=True)

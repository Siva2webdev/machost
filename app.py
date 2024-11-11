from flask import Flask, render_template, request
import hashlib
import requests
import json

app = Flask(__name__)

# MAC and device handling functions
def mac_to_var(mac):
    return mac.replace(":", "")

def generate_md5(mac):
    return hashlib.md5(mac.encode()).hexdigest()

def generate_sha256(input_str):
    return hashlib.sha256(input_str.encode()).hexdigest()

def convert_to_uppercase(data):
    return data.upper()

# API request handling functions
def make_get_request(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise HTTPError for bad responses
        if not response.text.strip():  # If the response body is empty
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

# API functions for each genre type
def get_device_info(host, mac):
    url = f"http://{host}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml&mac={mac}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Host': host}
    return make_get_request(url, headers)

def get_genres(host, mac):
    url = f"http://{host}/portal.php?type=itv&action=get_genres&JsHttpRequest=1-xml&mac={mac}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Host': host}
    return make_get_request(url, headers)

def vod_genres(host, mac):
    url = f"http://{host}/portal.php?type=vod&action=get_categories&JsHttpRequest=1-xml&mac={mac}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Host': host}
    return make_get_request(url, headers)

def series_genres(host, mac):
    url = f"http://{host}/portal.php?type=series&action=get_categories&JsHttpRequest=1-xml&mac={mac}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Host': host}
    return make_get_request(url, headers)

# Function to parse and display results
def parse_device_info(response_json):
    device_info = response_json.get("js", {}, 'Expiry')
    return json.dumps(device_info, indent=4) if device_info else "No device information found."

def parse_genres(response_json):
    genre_list = response_json.get("js", [])
    return ", ".join([entry['title'] for entry in genre_list]) if genre_list else "No genres found."

def parse_vod_genres(response_json):
    vod_list = response_json.get("js", [])
    return ", ".join([entry['title'] for entry in vod_list]) if vod_list else "No VOD genres found."

def parse_series_genres(response_json):
    series_list = response_json.get("js", [])
    return ", ".join([entry['title'] for entry in series_list]) if series_list else "No series genres found."

# Define your routes
@app.route('/', methods=['GET', 'POST'])
def home():
    device_info = ''
    genres = ''
    vod_genres = ''
    series_genres = ''
    error_message = ''  # Initialize error_message as an empty string

    if request.method == 'POST':
        host = request.form['url']
        mac = request.form['mac']

        mac_var = mac_to_var(mac)
        sn = generate_md5(mac)
        sn_enc = convert_to_uppercase(sn)
        dev = generate_sha256(mac)
        dev_enc = convert_to_uppercase(dev)

        # Fetch device info and genres
        device_info = get_device_info(host, mac)
        if device_info:
            device_info = parse_device_info(device_info)
        else:
            error_message = "Device information not found or API not working."  # Set error message if device info retrieval fails

        genres = get_genres(host, mac)
        if genres:
            genres = parse_genres(genres)
        vod_genres = get_genres(host, mac)
        if vod_genres:
            vod_genres = parse_genres(vod_genres)
        series_genres = get_genres(host, mac)
        if series_genres:
            series_genres = parse_genres(series_genres)

    return render_template('index.html', device_info=device_info, genres=genres, vod_genres=vod_genres, series_genres=series_genres, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)

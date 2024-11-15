from flask import Flask, render_template, request, jsonify
import hashlib
import requests
import json

app = Flask(__name__)

# Helper functions for hash generation based on MAC
def generate_hashes(mac):
    sn = hashlib.md5(mac.encode('utf-8')).hexdigest().upper()
    sn_cut = sn[:13]  # First 13 characters for SNENC
    dev = hashlib.sha256(mac.encode('utf-8')).hexdigest().upper()
    sg = sn_cut + '+' + mac
    sing = hashlib.sha256(sg.encode('utf-8')).hexdigest().upper()
    return {
        'SN': sn,
        'SN_CUT': sn_cut,
        'DEV_1': dev,
        # 'DEV_2': sing
    }

# API request handling functions
def make_get_request(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

# API functions for device info and genre data
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

# Function to create ITV link
# def create_itv_link(host, mac):
#     url = f"http://{host}/portal.php?action=create_link&type=itv&cmd=ffmpeg%20http://localhost/ch/106_&JsHttpRequest=1-xml&mac={mac}"
#     headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Host': host}
#     return make_get_request(url, headers)

# Function to parse API responses
def parse_genres(response_json):
    genre_list = response_json.get("js", [])
    return ", ".join([entry['title'] for entry in genre_list]) if genre_list else "No genres found."

# Route to handle form submission and display results
@app.route('/', methods=['GET', 'POST'])
def home():
    device_info = ''
    genres = ''
    vod_genres_list = ''
    series_genres_list = ''
    # itv_link_info = ''
    error_message = ''
    hashes = {}

    if request.method == 'POST':
        host = request.form['url']
        mac = request.form['mac']

        # Generate unique hashes based on MAC address
        hashes = generate_hashes(mac)

        # Fetch device info and genres
        device_info_response = get_device_info(host, mac)
        if device_info_response:
            device_info = json.dumps(device_info_response.get("js", {}), indent=4)
        else:
            error_message = "Device information not found or API not working."

        # Fetch and parse genres data
        genres_response = get_genres(host, mac)
        genres = parse_genres(genres_response) if genres_response else "No genres found."

        vod_genres_response = vod_genres(host, mac)
        vod_genres_list = parse_genres(vod_genres_response) if vod_genres_response else "No VOD genres found."

        series_genres_response = series_genres(host, mac)
        series_genres_list = parse_genres(series_genres_response) if series_genres_response else "No series genres found."

        # Fetch ITV link information
        # itv_link_response = create_itv_link(host, mac)
        # itv_link_info = json.dumps(itv_link_response, indent=4) if itv_link_response else "ITV link creation failed."

    return render_template(
        'index.html',
        device_info=device_info,
        genres=genres,
        vod_genres=vod_genres_list,
        series_genres=series_genres_list,
        # itv_link_info=itv_link_info,
        error_message=error_message,
        hashes=hashes
    )

if __name__ == '__main__':
    app.run(debug=True)

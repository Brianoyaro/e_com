from flask import Blueprint, request
import requests
from requests.auth import HTTPBasicAuth


mpesa = Blueprint('mpesa', __name__)

# mpesa details
consumer_key = 'ctuHOp1Aji1y9I8KvlNgreBzdChFdXzbhVZ0drGh9CYw6MMz'
consumer_secret = 'c4kfyzIO2bYSghcHQOHzsMjNngnIYLAlPvp6XABv6KWXGOCKsvJ3sfw4aWx5LAZj'
base_url = 'https://4938-102-222-145-50.ngrok-free.app' # use ngrok url

# generate access token
def generate_token():
    '''generate mpesa access token'''
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.json()['access_token']

# simulate stk push
@mpesa.route('/simulate')
def sim_stk_push():

    phone_number = 254722474626
    till_number = 174379

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + generate_token()
    }
    # functin to generate timestamp
    def generate_timestamp():
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return timestamp
    
    # function to generate password
    def generate_password():
        import base64
        timestamp = generate_timestamp()
        # password = BusinessShortCode + Lipa Na Mpesa Online Passkey + Timestamp
        password = '174379' + '174379' + generate_timestamp()
        encoded = base64.b64encode(password.encode())
        return encoded.decode('utf-8')
    
    payload = {
        "BusinessShortCode": till_number,
        "Password": generate_password(),
        "Timestamp": generate_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": phone_number,
        "PartyB": till_number,
        "PhoneNumber": phone_number,
        "CallBackURL": base_url + '/validate-stk',
        "AccountReference": "My Company",
        "TransactionDesc": "Payment of Goods and Services" 
    }

    response = requests.post( url, headers=headers, json=payload)
    return response.json()

# validate stk push
@mpesa.route('/validate-stk', methods=['POST'])
def validate_stk():
    # print(request.json)
    response = request.json()
    callback_metadata = response.get('Body').get('stkCallback').get('CallbackMetadataa', None)
    # error or user cancelled transaction
    if not callback_metadata:
        return 'Invalid response'
    # save the response to the database, create a new order object and save the transaction
    return 'success'
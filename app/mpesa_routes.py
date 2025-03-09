from flask import Blueprint, request
import requests
from requests.auth import HTTPBasicAuth
from . import db
import json

mpesa = Blueprint('mpesa', __name__)

# Steps
#_____________________________________________________________________________________________________________________
# 1. Generate access token
# 2. Register urls
# 3. Handle confirmation and validation urls


# mpesa details
consumer_key = 'ctuHOp1Aji1y9I8KvlNgreBzdChFdXzbhVZ0drGh9CYw6MMz'
consumer_secret = 'c4kfyzIO2bYSghcHQOHzsMjNngnIYLAlPvp6XABv6KWXGOCKsvJ3sfw4aWx5LAZj'
base_url = 'https://4938-102-222-145-50.ngrok-free.app' # use ngrok url

def generate_token():
    '''generate mpesa access token'''
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.json()

'''# access token
@mpesa.route('/access_token', methods=['GET'])
def get_access_token():
    access_token = generate_token()
    return access_token

# register urls
@mpesa.route('/register_urls')
def register_urls():
    mpesa_auth_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
    headers = {
        'Authorization': 'Bearer ' + generate_token()['access_token'],
        'Content-Type': 'application/json'
    }
    response = requests.post(
        mpesa_auth_url,
        headers=headers, 
        json={
            'ShortCode': '600998',
            'ResponseType': 'Completed',
            'ConfirmationURL': base_url + '/confirmation',
            'ValidationURL': base_url + '/validation'
        }
    )                     
    return response.json()'''

# confirmation url
@mpesa.route('/confirmation', methods=['POST'])
def confirmation():
    data = request.get_json()
    # save to db or file
    # with open('confirmation.json', 'a') as f:
    #     f.write(json.dumps(data))
    print(f"Confirmation: {data}")
    return {
        'ResultCode': 0,
        'ResultDesc': 'Accepted'
    }

# validation url
@mpesa.route('/validation', methods=['POST'])
def validation():
    data = request.get_json()
    # save to db or file
    # with open('validation.json', 'a') as f:
    #     f.write(json.dumps(data))
    print(f"Validation: {data}")
    return {
        'ResultCode': 0,
        'ResultDesc': 'Accepted'
    }

# simulate stk push
@mpesa.route('/simulate')
def sim_stk_push():
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + generate_token()['access_token']
    }
    payload = {
        "BusinessShortCode": 174379,
        "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjUwMzA5MDY0NzE4",
        "Timestamp": "20250309064718",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": 254722474626,
        "PartyB": 174379,
        "PhoneNumber": 254722474626,
        "CallBackURL": base_url + '/validation',
        "AccountReference": "CompanyXLTD",
        "TransactionDesc": "Payment of X" 
    }

    response = requests.post( url, headers=headers, json=payload)
    return response.json()

# stk push
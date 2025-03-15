from flask import Blueprint, request, jsonify
import requests
from requests.auth import HTTPBasicAuth


mpesa = Blueprint('mpesa', __name__)

# mpesa details
consumer_key = 'ctuHOp1Aji1y9I8KvlNgreBzdChFdXzbhVZ0drGh9CYw6MMz'
consumer_secret = 'c4kfyzIO2bYSghcHQOHzsMjNngnIYLAlPvp6XABv6KWXGOCKsvJ3sfw4aWx5LAZj'
base_url = 'https://0a14-102-222-145-50.ngrok-free.app' # use ngrok url

# generate access token
def generate_token():
    '''generate mpesa access token'''
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.json()['access_token']

# simulate stk push
@mpesa.route('/simulate', methods=['GET', 'POST'])
def sim_stk_push():
    # data = request.get_json()
    # phone_number = data.get('phone_number')           ---->to send STK-push
    # amount = data.get('amount')
    # email = data.get('email')           ---> to save in db
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
        password = '174379' + 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919' + generate_timestamp()
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
    print(payload)

    response = requests.post( url, headers=headers, json=payload)
    # print("MPESA Response Status:", response.status_code)
    # print("MPESA Response Headers:", response.headers)
    # print("MPESA Response Text:", response.text)
    return response.json()

'''# validate stk push
@mpesa.route('/validate-stk', methods=['GET', 'POST'])
def validate_stk():
    print("Request.values:", request.values)
    print(f"(Request.json): {request.json()}")
    print(dir(request))
    response = request.get_json()
    print(f"Response: {response}")
    # print(f"Response: {response}")
    # if not response:
    #     return {'message': 'failed', 'error': 'No JSON received'}, 400  # Return error response

    # callback_metadata = response.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', None)

    # if not callback_metadata:
    #     return {'message': 'failed', 'error': 'Callback metadata missing'}, 400  # Return error response
    
    # return {'message': 'success', 'data': callback_metadata['Item']}
    return response'''

@mpesa.route('/validate-stk', methods=['POST'])
def validate_stk():
    data = request.get_json()

    # Extract the required fields
    stk_callback = data.get("Body", {}).get("stkCallback", {})
    merchant_request_id = stk_callback.get("MerchantRequestID")
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")

    # Initialize transaction details
    transaction_details = {
        "Amount": None,
        "MpesaReceiptNumber": None,
        "TransactionDate": None,
        "PhoneNumber": None
    }

    # Extract CallbackMetadata items
    callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
    for item in callback_metadata:
        transaction_details[item["Name"]] = item.get("Value")

    # Log transaction
    print(f"Transaction Response: {transaction_details}")

    # Handle transaction success/failure
    if result_code == 0:
        # Save transaction to database (Example)
        # save_transaction(transaction_details)  # Implement this function
        response_message = "Transaction received successfully"
    else:
        response_message = f"Transaction failed: {result_desc}"

    return jsonify({"message": response_message}), 200
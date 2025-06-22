import requests

def send_sms(mobile_number,message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    api_key = "JfHLaXt7gAGru2BNh3FzydDSjEqm0oITeKi8PYkQv16WpswM4Zjv5bJGs6hFxg9ocXuw7BVn8DaSdT4t"
    
    headers = {
        'authorization': api_key,
        'Content-Type': "application/json"
    }

    payload = {
        "route": "q",
        "sender_id": "TXTIND",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": mobile_number
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response:", response.json())
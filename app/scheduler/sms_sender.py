from twilio.rest import Client

# Twilio credentials (store securely in env or config)
ACCOUNT_SID = 'your_account_sid'
AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE = '+1234567890'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(to_number, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=to_number
        )
        print(f"Message sent to {to_number}")
    except Exception as e:
        print(f"Failed to send SMS to {to_number}: {e}")


######  --------   Just an template code to send message using twillio -------- ######### 
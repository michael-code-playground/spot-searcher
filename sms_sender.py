import webbrowser

# Phone number and message
phone_number = "+1234567890"
message = "Hello from my Python app!"

# Construct the SMS URL
sms_url = f'sms:{phone_number}?body={message}'

# Open the default SMS app with pre-filled number and message
webbrowser.open(sms_url)

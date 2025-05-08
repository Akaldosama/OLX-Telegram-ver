import requests


def send_message_to_seller(seller_telegram_id, buyer_name, buyer_phone, product_title):
    # Replace with your bot token
    bot_token = '7758239108:AAHnLTmadRdpfe4C60V6-5P_0b2RvqpGrAU'

    # Construct the message
    message = (
        f"Hi there!\n"
        f"{buyer_name} ({buyer_phone}) wants to buy your product: '{product_title}'\n"
        f"Contact the buyer for further details."
    )

    # Define the URL for sending messages through the Telegram Bot API
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Set the parameters for the API request
    params = {
        'chat_id': seller_telegram_id,
        'text': message,
        'parse_mode': 'Markdown'  # Use markdown formatting
    }

    # Send the message
    response = requests.post(url, params=params)

    # Optionally check the response
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
    else:
        print("Message sent successfully.")

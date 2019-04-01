from twilio.rest import Client

def send_sms():
    account_sid = 'AC5211776013073aaea06172b116868a24'
    auth_token = 'a078d012f53238b2e35ff782f75ee79a'
    client = Client(account_sid, auth_token)

    sms = client.messages \
            .create(
                body="Thanks for signing up with SellFast",
                from_='+12015716848',
                to='+60122220899'
            )

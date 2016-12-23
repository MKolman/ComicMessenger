import sys
import traceback

from getpass import getpass
from fbchat import Client
from feeder import message_creator


def send_result(client, user, data):
    """ Send a single new comic to a user
    :params:
        client: a fbchat.Client instance ready to send messages
        user: a Facebook user id
        data: a dictionary describing the message
    """
    if "img" in data:
        if "pre" not in data: data["pre"] = ""
        client.sendRemoteImage(user, message=data["pre"], image=data["img"])
    if "post" in data:
        client.send(user, data["post"])


def send_all(username=None, password=None, subscribers=None):
    """ Send all new comics from username to all subscribers
    :params:
        username: Facebook username (email, phone number or some other id)
        password: Facebook account password
        subscribers: All the people that will receive the update
    """
    if not username:
        username = input("Enter username: ")
    if not password:
        password = getpass()
    try:
        print("Logging in...")
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"
        client = Client (username, password, debug=False, user_agent=ua)
    except Exception as e:
        print("Could not login!")
        print(traceback.format_exc())
        return False

    if not subscribers:
        subscribers = [input("Send to: ")]
    users = [int(user) if str(user).isdecimal() else
             client.getUsers(user)[0].uid for user in subscribers]
    first_message = True
    try:
        for message in message_creator(True):
            for user in users:
                if first_message:
                    client.send(user, "Hey, I have new comics for you!")
                send_result(client, user, message)
            first_message = False
        if first_message:
            for user in users:
                client.send(user, "Sorry, no new comics at this time.")
    except Exception as e:
        exc = traceback.format_exc()
        print("Comic Messenger failed")
        print(exc)
        for user in users:
            client.send(user, "Comic sender failed. Sorry.")
            client.send(user, exc)


if __name__ == "__main__":
    username, password = None, None
    if len(sys.argv) >= 2:
        username = sys.argv[1]
    if len(sys.argv) >= 3:
        password = sys.argv[2]

    subscribers = ["Maks Kolman"]
    send_all(username, password, subscribers)

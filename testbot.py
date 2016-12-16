import fbchat
from getpass import getpass


# subclass fbchat.Client and override required methods
class TestBot(fbchat.Client):

    def __init__(self, email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self, email, password, debug, user_agent)

    def on_message(self, mid, author_id, author_name, message, metadata):

        thread_id = metadata["delta"]["messageMetadata"]["threadKey"]
        print("%s said (in %s): %s" % (author_id, thread_id, message))
        message_type = "user"
        if "threadFbId" in thread_id:
            thread_id = thread_id["threadFbId"]
            message_type = "group"
        else:
            thread_id = thread_id["otherUserFbId"]

        if message.lower().endswith("test"):
            self.send(thread_id, "is", message_type=message_type)


client = TestBot("max-maks@hotmail.com", getpass(), debug=False)
client.listen()

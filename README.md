# ComicMessenger
A Facebook messenger bot for sending the newest comics to users. It will send you a Facebook message with any new comic you desire.

### Notice
Please be careful when using this code as it can be very easy to accidentally
send A LOT of messages. I have not yet encountered this, but it may be possible
for Facebook to detect you as a spam account and block you.

## Setup
```bash
sudo apt-get install libxml2-dev libxslt-dev gcc
git clone https://github.com/MKolman/ComicMessenger.git
cd ComicMessenger
virtualenv -p $(which python3) venv
source venv/bin/activate
pip install -r requirements.txt
```
### Warning
The `fbchat` library has a bug in python 3.5 causing it to crash when sending
images. You have to add two lines into
`venv/lib/python3.5/site-packages/fbchat/client.py` under the line 325:

```python
r = self._postFile(UploadURL, image)
if isinstance(r._content, bytes):               # New line
    r._content = r._content.decode("utf-8")     # New line
# Strip the start and parse out the returned image_id
return json.loads(r._content[9:])['payload']['metadata'][0]['image_id']
```

## Running
To run the program you have to enter the python virtual environment and run the
script.

```bash
source venv/bin/activate
python main.py [fb_username [fb_password]]
```
You can provide your username and password directly when running or wait for
the prompt by the program.

You can change the list of subscribers in the list at the bottom of `main.py`.

### Crontab
To run this script every day at 06:00 (computer time) open crontab
```bash
crontab -e
```
and add the following line
```
0 6 * * * cd /path/to/ComicMessenger/ && . venv/bin/activate && python main.py <username> <password> >> crontab.log
```

## Currently supported comics
Current implementation includes:
 - XKCD (http://xkcd.com/)
 - Cyanide & Happiness (http://explosm.net/comics/latest/)
 - Saturday Morning Breakfast Cereal (http://www.smbc-comics.com/)
 - PhD comics (http://phdcomics.com/comics.php)

## Contribute
To contribute a new comic to the collection all you have to do is add its
RSS link in `feeder.py` and add a parser for your comic in `def parser`.
Then send me a pull request.

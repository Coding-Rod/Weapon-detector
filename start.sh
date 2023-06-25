# Install curl if not installed
if ! [ -x "$(command -v curl)" ]; then
  sudo apt-get install curl
fi

base64 images/sample.jpg | curl -d @- \
"http://localhost:9001/knives-n-guns-backup/1?api_key=uWT4WzrPNeKaypAQ3Ah7"

sudo python3 app.py

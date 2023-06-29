# Install curl if not installed
if ! [ -x "$(command -v curl)" ]; then
  sudo apt-get install curl
fi

base64 images/sample.jpg | curl -d @- \
"http://localhost:9001/weapons-28-jun/4?api_key=7rRyq2IXnl3yEIKk7GCw"

python3 app.py

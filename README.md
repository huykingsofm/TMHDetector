# Usage
## Installation
You will need to:
- Install latest version of [Google Chrome](https://www.google.com/chrome/).
- Install [Python3-64bit](https://www.python.org/downloads/).  

On Windows
```bash
# Set up a virtual enviroment
$ python -m venv env
$ .\env\Scripts\activate

# Install require packages
$ python install -r requirements.txt
```

On Linux
```bash
# Set up a virtual env
$ python3 -m venv env
$ source ./venv/bin/activate

# Install Python requirements
$ pip install -r requirements.txt
```

## How to run  
On Server machine
- Fill all facebook accounts (email and password) into [`credentials.yaml`](.\credentials.yaml) to serve crawling
- Fill ip and port of server into [`credentials.yaml`](.\credentials.yaml)
```bash
$ python Server.py
```

On Client machine
```bash
# Read usage of Client.py
$ python Client.py --help

# Common usage, fb_id is facebook url or facebook id of profile which you want to detect
$ python Client.py fb_id

# or
$ python Client.py fb_id --ip 10.0.0.1 --port 13579
```
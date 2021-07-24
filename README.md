# Archonia Stalker
Do you want to stalk your archonia wishlist without putting in any effort then this is perfect for you.

## Setup
To get started, create a virtual environment with python.
```
python -m venv archonia --upgrade-deps
```
Activate the archonia environment.
```
.\archonia\Scripts\activate    
```
Then, install the dependencies from the `requirements.txt`.
```
pip install -r .\requirements.txt 
```
To make use of this scraper you need to fill in the `settings.yaml`.
```
WISHLIST: ''
EMAIL: ''
PASSWORD: ''
WEBHOOK_URL: ''
DISCORD_MENTION: ''
```

## Running
To run this application you can use the following command.
```
scrapy runspider main.py
```

To make this task recurring you can setup a cronjob.

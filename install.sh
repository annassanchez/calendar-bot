python -m venv bot_env #creating the virtual enviroment
source bot_env/bin/activate #activate
pip install jupyter google-auth google-auth-oauthlib google-auth-httplib2 \
    google-api-python-client python-telegram-bot apscheduler
pip install ipykernel
python -m ipykernel install --user --name=bot_env --display-name "Python (bot_env)"
pip install -r /path/to/requirements.txt

#pip3 freeze > requirements.txt  # Python3
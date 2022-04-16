# Getting started with the Cama Community App For Discord

Run these commands to get Cama Community running locally:

```bash
virtualenv -p $PYTHON_PATH_39 venv39
source ./venv39/bin/activate
pip install -r requirements.txt

echo $"#/bin/sh\nblack .\npython lint.py -p ../cama-community/'> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Visit this URL to invite this bot to your server
https://discord.com/api/oauth2/authorize?client_id=964357127005171712&permissions=518633381313&scope=applications.commands%20bot

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
Dev:
# https://discord.com/api/oauth2/authorize?client_id=964357127005171712&permissions=518633381313&scope=applications.commands%20bot
Staging
# https://discord.com/api/oauth2/authorize?client_id=965707277673844776&permissions=380154010944&redirect_uri=https%3A%2F%2Fcama-community-staging.herokuapp.com%2Fdiscord&response_type=code&scope=applications.commands%20bot

To easily set config variables
```bash
heroku config:set $(cat .env | sed '/^$/d; /#[[:print:]]*$/d')
```
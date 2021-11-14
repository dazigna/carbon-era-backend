# INSTALL
## Install dependencies
Run `pip install -r requirements.txt` to install the project's deps.
## Update dependencies
Run `pip freeze > requirements.txt` to update deps.

# RUN
To start the server, you need to run this cmd :
```
FLASK_APP=./src/test_api/run.py FLASK_DEBUG=1 flask run
```
Then you'll find the Swagger UI at `http://127.0.0.1:5000/api/v1/ui/`

# REFS
Read more here : 
- https://haseebmajid.dev/blog/rest-api-openapi-flask-connexion
- https://github.com/zalando/connexion
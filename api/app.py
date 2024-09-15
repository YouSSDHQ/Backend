import os
import secrets
from dotenv import load_dotenv
from quart import Quart, g
from quart_schema import QuartSchema

from models.base import BaseResponse
from routes import misc, ussd
load_dotenv()


app = Quart("StellSSD")
QuartSchema(app, convert_casing=True)
secret_key = str(os.getenv(key="SECRET_KEY")).strip()
if len(secret_key) < 10:
    print("Generating a random secret key...")
    # Generate a random secret key if one is not provided
    secret_key = secrets.token_hex(nbytes=20)
    with open(".env", "a+") as f:
        f.write(f"\nSECRET_KEY={secret_key}\n")


app.config["SECRET_KEY"] = secret_key

@app.before_request
async def before_request():
    print("before request")
    print(g.__dict__)
    g.setdefault('user', None)

@app.errorhandler(Exception)
async def handle_error(error: Exception):
    print(error)
    return BaseResponse(message=str(error), status="error")

app.register_blueprint(misc.bp)
app.register_blueprint(ussd.bp)


@app.route("/")
async def index():
    return BaseResponse(message="hello")

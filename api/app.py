import os
import secrets
from pprint import pprint

from dotenv import load_dotenv
from quart import Quart, Response
from quart_schema import QuartSchema

from models.base import BaseResponse
from routes import misc, ussd

load_dotenv()


app = Quart("YouSSD")
QuartSchema(app, convert_casing=True)
secret_key = str(os.getenv(key="SECRET_KEY")).strip()
if len(secret_key) < 10:
    print("Generating a random secret key...")
    # Generate a random secret key if one is not provided
    secret_key = secrets.token_hex(nbytes=20)
    with open(".env", "a+") as f:
        f.write(f"\nSECRET_KEY={secret_key}\n")


app.config["SECRET_KEY"] = secret_key


@app.before_serving
async def before_serving():
    print("before serving")
    from services.database import init_db

    await init_db()


@app.after_request
async def aft_request(response: Response):
    print("after request")
    from services.ussd import session_cache

    print("Current session")
    pprint(session_cache, indent=3)
    return response


@app.errorhandler(Exception)
async def handle_error(error: Exception):
    print(error)
    return f"END An error occurred {str(error)}"


app.register_blueprint(misc.bp)
app.register_blueprint(ussd.bp)


@app.route("/")
async def index():
    return BaseResponse(message="hello")

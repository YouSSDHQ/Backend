
import os
import secrets
from typing import Dict, List
from quart import Blueprint, request, session, url_for
from quart import Quart
import requests
from quart_schema import DataSource, validate_request

from models.ussd import UssdRequest
from services.ussd import process_request

app = Quart(__name__)

bp = Blueprint("ussd", __name__, url_prefix="")

@bp.route("/ussd", methods=["POST"])
@validate_request(UssdRequest, source=DataSource.FORM)
async def ussd_callback(data: UssdRequest):
    """
    Handle USSD callback

    Returns:
        str: response message
    """

    # print session ID and request data
    print(session.get("at_session_id"))
    print(f"{data=}")

    # get request parameters
    session_id = data.session_id
    service_code = data.service_code
    phone_number = data.phone_number
    text = data.text
    print(f"{session_id=} {service_code=} {phone_number=} {text=}")

    # set session ID if not already set
    if not session.get("user"):
        session["user"] = session_id
    print(session.get("user"))

    # process USSD text
    words, length = process_request(text)
    print(f"{words=} {length=}")
    if length == 1:
        if words[0] == "":
            return "CON Hi, welcome to Ite. What would you like to do?\n1. Sign up\n2. Eat me"
        if words[0] == "1":
            return "END I will bite you"
        
    if length == 2:
        return "CON How may I help you?"
    return "END Bye"

@app.route("/health")
async def health():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
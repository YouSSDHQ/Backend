from quart import Blueprint
from quart_schema import DataSource, validate_request

from models.ussd import UssdRequest
from services.ussd import process_request

bp = Blueprint("ussd", __name__, url_prefix="")


@bp.route("/ussd", methods=["POST"])
@validate_request(UssdRequest, source=DataSource.FORM)
async def ussd_callback(data: UssdRequest):
    """
    Handle USSD callback

    Returns:
        str: response message
    """

    # Log request data
    print(f"{data=}")
    print(
        f"session_id='{data.session_id}' service_code='{data.service_code}' phone_number='{data.phone_number}' text='{data.text}'"
    )

    # Process the USSD request
    response = await process_request(data)

    return response

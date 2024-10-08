from quart import Blueprint
from quart_schema import validate_request, validate_response

from models.waitlist import WaitlistJoinRequest, WaitlistJoinResponse
from services.database import get_session
from services.user import UserService


bp = Blueprint("waitlist", __name__)


@bp.route("/waitlist", methods=["POST"])
@validate_request(WaitlistJoinRequest)
@validate_response(WaitlistJoinResponse)
async def waitlist(data: WaitlistJoinRequest):
    """
    Handle waitlist join request

    Returns:
        str: response message
    """

    print(f"email='{data.email}' phone_number='{data.phone_number}'")
    async with get_session() as sess:
        user_service = UserService(sess)
        status, message = await user_service.add_to_waitlist(data)

    return WaitlistJoinResponse(message=message), status

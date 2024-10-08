from quart import Blueprint
from quart_schema import DataSource, validate_request, validate_response

from models.waitlist import WaitlistJoinRequest, WaitlistJoinResponse
from services.database import get_session
from services.user import UserService


bp = Blueprint("waitlist", __name__)


@bp.route("/waitlist", methods=["POST"])
@validate_request(WaitlistJoinRequest, source=DataSource.JSON)
@validate_response(WaitlistJoinResponse)
async def waitlist(data: WaitlistJoinRequest):
    """
    Handle waitlist join request

    Returns:
        str: response message
    """

    print(f"phone_number='{data.phone_number}'")
    async with get_session() as sess:
        user_service = UserService(sess)
        status, message = await user_service.add_to_waitlist(data)
    print(f"status='{status}' message='{message}'")
    return WaitlistJoinResponse(message=message), int(status)

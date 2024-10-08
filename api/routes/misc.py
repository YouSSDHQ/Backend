from quart import Blueprint, request

bp = Blueprint("misc", __name__, url_prefix="")


@bp.route("/logs", methods=["POST"])
async def logs():
    data = await request.get_json()
    print(f"data: {data}")
    logs = await request.values
    print(f"logs: {logs}")
    return "pong"


@bp.route("/health")
async def health():
    return "OK"

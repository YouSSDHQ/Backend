from datetime import datetime, timedelta
from typing import Dict

from solders.pubkey import Pubkey

from models.ussd import UssdRequest
from services.database import get_session
from services.transfer import SolanaTransfer
from services.user import UserService

# Initialize in-memory cache
session_cache = {}

# Add these to your existing imports and global variables
sol_transfer = SolanaTransfer(os.getenv("RPC_URL"))


def get_session_data(session_id: str) -> Dict:
    """Retrieve session data from memory cache"""
    return session_cache.get(session_id, {})


def set_session(session_id: str, data: Dict):
    """Store session data in memory cache"""
    session_cache[session_id] = data


def delete_session(session_id: str):
    """Delete session data from memory cache"""
    if session_id in session_cache:
        del session_cache[session_id]


async def process_request(data: UssdRequest) -> str:
    """Main function to process USSD requests"""
    session_data = get_session_data(data.session_id)
    state = session_data.get("state", "initial")

    if state == "initial":
        return await handle_initial_state(data)
    elif state == "existing_user":
        return await handle_existing_user(data)
    elif state == "signup_username":
        return await handle_signup_username(data)
    elif state == "wallet_access":
        return await handle_wallet_access(data)
    elif state == "view_balance":
        return await handle_view_balance(data)
    elif state == "send_tokens":
        return await handle_send_tokens(data)
    else:
        return "END An error occurred. Please try again."


async def handle_wallet_access(data: UssdRequest) -> str:
    set_session(data.session_id, {"state": "wallet_access"})
    response = data.text.split("*")[-1]
    if response == "1":
        return await handle_view_balance(data)
    elif response == "2":
        return "CON Coming Soon!"
    elif response == "3":
        set_session(data.session_id, {"state": "initial"})
        return "CON Wallet Access:\n1. View Balance\n2. Send sol\n3. Back to Main Menu"
    else:
        return "END An error occurred. Please try again."


async def handle_existing_user(data: UssdRequest) -> str:
    response = data.text.split("*")[-1]
    if response == "2":
        delete_session(data.session_id)
        return "END Thank you for using YouSSD. Goodbye!"
    elif response == "1":
        set_session(data.session_id, {"state": "wallet_access"})
        return "CON Wallet Access:\n1. View Balance\n2. Send sol\n3. Back to Main Menu"


async def handle_view_balance(data: UssdRequest) -> str:
    async with get_session() as sess:
        user_service = UserService(sess)
        user = await user_service.get_user_by_phone_number(data.phone_number)

        if not user:
            return "END Please sign up first."

        if user.last_balance_update is None and user.sol_balance == 0:
            balance = await sol_transfer.get_solana_balance(
                Pubkey.from_string(user.public_key)
            )
            user.last_balance_update = datetime.now()
            user.sol_balance = balance
            await sess.commit()  # No need to add user again, as it's already tracked

        elif user.last_balance_update and (
            datetime.now() - user.last_balance_update
        ) < timedelta(seconds=10):
            balance = user.sol_balance
        else:
            balance = await sol_transfer.get_solana_balance(
                Pubkey.from_string(user.public_key)
            )
            user.last_balance_update = datetime.now()
            user.sol_balance = balance
            await sess.commit()
        delete_session(data.session_id)

    return f"END Your balance is: {balance} SOL"


async def handle_send_tokens(data: UssdRequest) -> str:  # TODO
    session_data = get_session_data(data.session_id)
    user_id = session_data.get("user_id")
    if not user_id:
        return "END Please sign up first."

    parts = data.text.split("*")
    if len(parts) == 2:
        set_session(data.session_id, {"state": "send_tokens", "recipient": parts[1]})
        return "CON Enter amount to send (in SOL):"
    elif len(parts) == 3:
        recipient = session_data.get("recipient")
        amount = float(parts[2])

        # Retrieve sender's keypair and recipient's public key
        sender_keypair = get_user_keypair(user_id)
        recipient_pubkey = get_user_public_key(recipient)

        try:
            tx_signature = await sol_transfer.send_sol(
                sender_keypair, Pubkey.from_string(recipient_pubkey), amount
            )
            set_session(data.session_id, {"state": "initial"})
            return (
                f"END Tokens sent successfully. Transaction signature: {tx_signature}"
            )
        except Exception as e:
            set_session(data.session_id, {"state": "initial"})
            return f"END Failed to send tokens: {str(e)}"
    else:
        return "END Invalid input. Please try again."


async def handle_initial_state(data: UssdRequest) -> str:
    """Handle the initial state of the USSD session"""
    if data.text == "":
        async with get_session() as sess:
            user_service = UserService(sess)
            existing_user = await user_service.get_user_by_phone_number(
                data.phone_number
            )

        if existing_user:
            set_session(
                data.session_id,
                {"user_id": existing_user.id, "state": "existing_user"},
            )
            return f"CON Welcome back {existing_user.username}.\nCurrent balance: {existing_user.sol_balance} SOL.\n\n What would you like to do?\n1. Access wallet\n2. Quit"
        else:
            set_session(data.session_id, {"state": "initial"})
        return "CON Welcome to YouSSD. What would you like to do?\n1. Sign up\n2. Access wallet"
    elif data.text == "1":
        set_session(data.session_id, {"state": "signup_username"})
        return (
            "CON Enter your desired username and full name\ne.g 'idris_cool, Ade Obi':"
        )
    elif data.text == "2":
        set_session(data.session_id, {"state": "wallet_access"})
        return (
            "CON Wallet Access:\n1. View Balance\n2. Send Tokens\n3. Back to Main Menu"
        )
    else:
        delete_session(data.session_id)
        return "END Invalid input. Please try again."


async def handle_signup_username(data: UssdRequest) -> str:
    """Handle the username input during signup"""
    text = data.text.split("*")[-1]
    if "," not in text:
        return "END Expected format 'username, full name'\n\te.g 'idris_cool, Ade Obi'"
    username, full_name = text.split(",")[:2]
    if await validate_username(username):
        async with get_session() as sess:
            user_service = UserService(sess)
            # create wallet for user
            user_dict = {
                "username": username.strip(),
                "full_name": full_name.title().strip(),
                "phone_number": data.phone_number,
            }
            user = await user_service.create_user(user_dict)
        if isinstance(user, str):
            return user
        if user is None:
            delete_session(data.session_id)
            return "END An error occurred during signup. Please try again."

        delete_session(data.session_id)
        return f"END Thank you for signing up, {username}!\nYour account has been created.\nYour public key is: \n{user.public_key[:20]}\n{user.public_key[20:]}"
    else:
        return "CON Invalid username. Please try again."


async def validate_username(username: str) -> bool:
    """Validate the username"""
    # Add your validation logic here
    return len(username) >= 3 and username.isalnum()


async def get_user_keypair(user_id: int):
    pass


async def get_user_public_key(user_id: int) -> str:
    pass

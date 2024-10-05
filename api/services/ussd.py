from datetime import datetime, timedelta
from typing import Dict

from solders.pubkey import Pubkey

from models.ussd import UssdRequest
from services.database import get_session
from services.transfer import SolanaTransfer
from services.user import UserService

# Initialize in-memory cache
session_cache = {}  # TODO: replace with redis

# Add these to your existing imports and global variables
sol_transfer = SolanaTransfer(os.getenv("RPC_URL"))


def get_session_data(session_id: str) -> Dict:
    """Retrieve session data from memory cache"""
    return session_cache.get(session_id, {})


def set_session(session_id: str, data: Dict):
    """Store session data in memory cache"""
    if session_id not in session_cache:
        session_cache[session_id] = data
        return

    session_cache[session_id].update(data)


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
    elif state == "send_tokens":
        return await handle_send_tokens(data)
    elif state == "send_tokens_recipient":
        return await handle_send_tokens_amount(data)
    elif state == "send_tokens_confirm":
        return await handle_send_tokens_confirm(data)
    elif state == "view_balance":
        return await handle_view_balance(data)
    else:
        return "END An error occurred. Please try again."


async def handle_wallet_access(data: UssdRequest) -> str:
    set_session(data.session_id, {"state": "wallet_access"})
    response = data.text.split("*")[-1]
    if response == "1":
        return await handle_view_balance(data)
    elif response == "2":
        set_session(data.session_id, {"state": "send_tokens"})
        return "CON Enter the recipient's username:"
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
            await sess.commit()

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


# region send tokens
async def handle_send_tokens(data: UssdRequest) -> str:
    """Handles the initial stage of sending tokens, requesting the recipient."""
    session_data = get_session_data(data.session_id)
    user_id = session_data.get("user_id")
    if not user_id:
        return "END Please sign up first."

    parts = data.text.split("*")
    if len(parts) == 3:
        recipient = parts[-1]
        set_session(
            data.session_id, {"state": "send_tokens_recipient", "recipient": recipient}
        )
        return f"CON Enter amount to send to {recipient} (in SOL):"
    else:
        return "END Invalid input. Please try again."


async def handle_send_tokens_amount(data: UssdRequest) -> str:
    """Handles the stage of receiving the amount to send."""
    session_data = get_session_data(data.session_id)
    user_id = session_data.get("user_id")
    recipient = session_data.get("recipient")
    if not user_id or not recipient:
        return "END An error occurred. Please try again."

    parts = data.text.split("*")
    try:
        amount = float(parts[-1])
        set_session(
            data.session_id,
            {"state": "send_tokens_confirm", "recipient": recipient, "amount": amount},
        )
        return f"CON Confirm sending {amount} SOL to {recipient}? \n1. Yes\n2. No"
    except Exception as e:
        print(str(e))
        return "END Invalid input. Please try again."


async def handle_send_tokens_confirm(data: UssdRequest) -> str:
    """Handles the stage of confirming the transaction."""
    session_data = get_session_data(data.session_id)
    user_id = session_data.get("user_id")
    recipient = session_data.get("recipient")
    amount = session_data.get("amount")
    if not user_id or not recipient or not amount:
        delete_session(data.session_id)
        return "END An error occurred. Please try again."

    parts = data.text.split("*")
    print(f"Parts: {parts}")
    if parts[-1] == "1":
        await finalize_transaction(data, user_id, recipient, amount)
    elif parts[-1] == "2":
        delete_session(data.session_id)
        return "END Transaction canceled."
    else:
        delete_session(data.session_id)
        return "END Invalid input. Please try again."


async def finalize_transaction(
    data: UssdRequest, user_id: int, recipient: str, amount: float
) -> str:
    """Finalizes the transaction by sending the tokens."""
    # Retrieve sender's keypair and recipient's public key
    sender_keypair = await get_user_keypair(user_id)
    recipient_pubkey = await get_user_public_key(recipient)

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

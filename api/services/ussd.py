from typing import Tuple, Dict
import uuid
from models.ussd import UssdRequest

# Initialize in-memory cache
session_cache = {}


def get_session(session_id: str) -> Dict:
    """Retrieve session data from memory cache"""
    return session_cache.get(session_id, {})


def set_session(session_id: str, data: Dict):
    """Store session data in memory cache"""
    session_cache[session_id] = data


def process_request(data: UssdRequest) -> str:
    """Main function to process USSD requests"""
    session_data = get_session(data.session_id)
    state = session_data.get("state", "initial")

    if state == "initial":
        return handle_initial_state(data)
    elif state == "signup_username":
        return handle_signup_username(data)
    elif state == "wallet_access":
        return handle_wallet_access(data)
    else:
        return "END An error occurred. Please try again."


def handle_wallet_access(data: UssdRequest) -> str:
    return "END Wallet access feature coming soon!"


def handle_initial_state(data: UssdRequest) -> str:
    """Handle the initial state of the USSD session"""
    if data.text == "":
        set_session(data.session_id, {"state": "initial"})
        return "CON Welcome to Blockchain USSD. What would you like to do?\n1. Sign up\n2. Access wallet"
    elif data.text == "1":
        set_session(data.session_id, {"state": "signup_username"})
        return "CON Enter your desired username:"
    elif data.text == "2":
        set_session(data.session_id, {"state": "wallet_access"})
        return "END Wallet access feature coming soon!"
    else:
        return "END Invalid input. Please try again."


def handle_signup_username(data: UssdRequest) -> str:
    """Handle the username input during signup"""
    username = data.text.split("*")[-1]
    if validate_username(username):
        user_id = create_user(username, data.phone_number)
        set_session(data.session_id, {"state": "initial", "user_id": user_id})
        return (
            f"END Thank you for signing up, {username}!\nYour account has been created."
        )
    else:
        return "END Invalid username. Please try again."


def validate_username(username: str) -> bool:
    """Validate the username"""
    # Add your validation logic here
    return len(username) >= 3 and username.isalnum()


def create_user(username: str, phone_number: str) -> str:
    """Create a new user in the database"""
    user_id = str(uuid.uuid4())
    # Add code here to store user in your database
    return user_id


def generate_mnemonic() -> str:
    """Generate a new mnemonic for the user"""
    # Implement mnemonic generation logic here
    return "example mnemonic phrase"


def encrypt_mnemonic(mnemonic: str, password: str) -> str:
    """Encrypt the mnemonic using the user's password"""
    # Implement encryption logic here
    return "encrypted_mnemonic"


def process_blockchain_transaction(user_id: str, transaction_data: Dict) -> str:
    """Process a blockchain transaction"""
    # Implement blockchain transaction logic here
    return "Transaction processed successfully"

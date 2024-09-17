from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID


class SolanaTransfer:
    """
    A class for handling Solana transactions and token operations.
    """

    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        """
        Initializes the SolanaTransfer class with a specified RPC URL.

        Args:
            rpc_url (str, optional): The URL of the Solana RPC node. Defaults to "https://api.devnet.solana.com".
        """
        self.client = AsyncClient(rpc_url)

    async def set_source_wallet(self, private_key: str):
        """
        Sets the source wallet for transactions using a private key.

        Args:
            private_key (str): The private key of the source wallet.

        Returns:
            Keypair: The Keypair object representing the source wallet.
        """
        return Keypair.from_base58_string(private_key)

    async def set_public_key(self, address: str):
        """
        Sets the public key for a wallet using its address.

        Args:
            address (str): The address of the wallet.

        Returns:
            Pubkey: The Pubkey object representing the wallet's public key.
        """
        return Pubkey.from_string(address)

    async def get_solana_balance(self, public_key: Pubkey):
        """
        Retrieves the SOL balance of a given public key.

        Args:
            public_key (Pubkey): The public key of the wallet.

        Returns:
            float: The SOL balance of the wallet.
        """
        balance = await self.client.get_balance(public_key)
        return float(balance.value) / 1e9

    async def send_sol(self, sender: Keypair, recipient: Pubkey, amount: float):
        """
        Sends SOL from the sender's wallet to the recipient's wallet.

        Args:
            sender (Keypair): The Keypair object representing the sender's wallet.
            recipient (Pubkey): The Pubkey object representing the recipient's wallet.
            amount (float): The amount of SOL to be sent.

        Returns:
            str: The transaction signature.
        """
        transaction = Transaction().add(
            transfer(
                TransferParams(
                    from_pubkey=sender.pubkey(),
                    to_pubkey=recipient,
                    lamports=int(amount * 1e9),
                )
            )
        )

        result = await self.client.send_transaction(transaction, sender)

        confirm = await self.check_transaction(result.value)
        return confirm

    async def set_spl_client(self, token_address: Pubkey, sender: Keypair):
        """
        Sets up a client for SPL token operations.

        Args:
            token_address (Pubkey): The public key of the token.
            sender (Keypair): The Keypair object representing the sender's wallet.

        Returns:
            Token: The Token client object.
        """
        return Token(
            conn=self.client,
            pubkey=token_address,
            program_id=TOKEN_PROGRAM_ID,
            payer=sender,
        )

    async def get_token_account(self, spl_client: Token, owner: Pubkey):
        """
        Retrieves or creates a token account for a given owner.

        Args:
            spl_client (Token): The Token client object.
            owner (Pubkey): The Pubkey object representing the owner's wallet.

        Returns:
            Pubkey: The public key of the token account.
        """
        accounts = await spl_client.get_accounts_by_owner(owner)
        if accounts.value:
            return accounts.value[0].pubkey
        return await spl_client.create_associated_token_account(owner)

    async def get_token_balance(self, spl_client: Token, token_account: Pubkey):
        """
        Retrieves the balance of a token account.

        Args:
            spl_client (Token): The Token client object.
            token_account (Pubkey): The public key of the token account.

        Returns:
            str: The balance of the token account as a string.
        """
        balance = await spl_client.get_balance(token_account)
        return balance.value.ui_amount_string

    async def send_spl_token(
        self,
        spl_client: Token,
        sender: Keypair,
        sender_token_account: Pubkey,
        recipient_token_account: Pubkey,
        amount: float,
    ):
        """
        Sends SPL tokens from the sender's token account to the recipient's token account.

        Args:
            spl_client (Token): The Token client object.
            sender (Keypair): The Keypair object representing the sender's wallet.
            sender_token_account (Pubkey): The public key of the sender's token account.
            recipient_token_account (Pubkey): The public key of the recipient's token account.
            amount (float): The amount of tokens to be sent.

        Returns:
            str: The transaction signature.
        """
        transaction = await spl_client.transfer(
            source=sender_token_account,
            dest=recipient_token_account,
            owner=sender,
            amount=int(amount * 1e9),
        )
        return str(transaction.value)

    async def check_transaction(self, signature: Signature):
        """
        Checks the status of a transaction.

        Args:
            signature (Signature): The signature of the transaction to be checked.

        Returns:
            str: The status of the transaction.
        """
        result = await self.client.confirm_transaction(signature)
        return result

    async def close(self):
        """
        Closes the Solana client connection.
        """
        await self.client.close()

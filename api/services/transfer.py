from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID


class SolanaTransfer:
    def __init__(self, rpc_url="https://api.mainnet-beta.solana.com"):
        self.client = AsyncClient(rpc_url)

    async def set_source_wallet(self, private_key: str):
        return Keypair.from_base58_string(private_key)

    async def set_public_key(self, address: str):
        return Pubkey.from_string(address)

    async def get_solana_balance(self, public_key: Pubkey):
        balance = await self.client.get_balance(public_key)
        return float(balance.value) / 1e9

    async def send_sol(self, sender: Keypair, recipient: Pubkey, amount: float):
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
        return Token(
            conn=self.client,
            pubkey=token_address,
            program_id=TOKEN_PROGRAM_ID,
            payer=sender,
        )

    async def get_token_account(self, spl_client: Token, owner: Pubkey):
        accounts = await spl_client.get_accounts_by_owner(owner)
        if accounts.value:
            return accounts.value[0].pubkey
        return await spl_client.create_associated_token_account(owner)

    async def get_token_balance(self, spl_client: Token, token_account: Pubkey):
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
        transaction = await spl_client.transfer(
            source=sender_token_account,
            dest=recipient_token_account,
            owner=sender,
            amount=int(amount * 1e9),
        )
        return str(transaction.value)

    async def check_transaction(self, signature: Signature):
        result = await self.client.confirm_transaction(signature)
        return result

    async def close(self):
        await self.client.close()

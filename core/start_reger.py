import json
from itertools import cycle

import aiofiles
import aiohttp
from eth_account import Account
from eth_account.account import LocalAccount
from eth_account.messages import encode_defunct

import config
from utils import logger, get_connector, get_ref_code


class Reger:
    def __init__(self,
                 private_key: str | None = None) -> None:
        self.account: LocalAccount = Account.create() if not private_key else Account.from_key(private_key=private_key)
        self.ref_code: str = ''

    async def get_sign_message(self,
                               client: aiohttp.ClientSession) -> str:
        r = await client.get(url='https://metadata.p.rainbow.me/v1/graph',
                             params={
                                 'query': 'query getPointsOnboardChallenge($address: String! $referral: String) { pointsOnboardChallenge(address: $address referral: $referral) }',
                                 'variables': json.dumps({
                                     "address": self.account.address,
                                     "referral": self.ref_code
                                 }).replace(' ', ''),
                                 'operationName': 'getPointsOnboardChallenge'
                             })

        return (await r.json())['data']['pointsOnboardChallenge']

    def get_sign(self,
                 sign_message: str) -> str:
        return Account.sign_message(signable_message=encode_defunct(primitive=sign_message.encode()),
                                    private_key=self.account.key).signature.hex()

    async def confirm_sign(self,
                           client: aiohttp.ClientSession,
                           sign: str) -> int:
        r = await client.post(url='https://metadata.p.rainbow.me/v1/graph',
                              json={
                                  'operationName': 'validatePointsSignature',
                                  'query': 'mutation validatePointsSignature($address: String!, $signature: String!, $referral: String) {\n  onboardPoints(address: $address, signature: $signature, referral: $referral) {\n    error {\n      type\n    }\n    meta {\n      distribution {\n        next\n      }\n      status\n    }\n    leaderboard {\n      stats {\n        total_users\n        total_points\n      }\n      accounts {\n        address\n        earnings {\n          total\n        }\n        ens\n        avatarURL\n      }\n    }\n    user {\n      onboarding {\n        earnings {\n          total\n        }\n        categories {\n          data {\n            usd_amount\n            total_collections\n            owned_collections\n          }\n          type\n          display_type\n          earnings {\n            total\n          }\n        }\n      }\n      referralCode\n      earnings {\n        total\n      }\n      stats {\n        position {\n          current\n        }\n      }\n    }\n  }\n}',
                                  'variables': {
                                      'address': self.account.address,
                                      'referral': self.ref_code,
                                      'signature': sign
                                  }
                              })

        return (await r.json())['data']['onboardPoints']['user']['earnings']['total']

    async def start_reger(self,
                          proxy: str | None = None) -> None:
        self.ref_code: str = await get_ref_code()

        async with aiohttp.ClientSession(connector=await get_connector(proxy=proxy),
                                         headers={
                                             'authorization': f'Bearer {config.BEARER_TOKEN}',
                                             'content-type': 'application/json'
                                         }) as client:
            sign_message: str = await self.get_sign_message(client=client)
            sign: str = self.get_sign(sign_message=sign_message)
            received_points: int = await self.confirm_sign(client=client,
                                                           sign=sign)

        async with aiofiles.open(file='registered.txt',
                                 mode='a',
                                 encoding='utf-8-sig') as file:
            await file.write(f'{self.account.address}:{self.account.key.hex()}:{self.ref_code}:{received_points}\n')

        logger.success(f'Successfully registered account {self.account.address} | {received_points}')


async def start_reger(software_method: int,
                      proxy: str | None = None,
                      proxies_cycled: cycle | None = None,
                      private_key: str | None = None) -> None:
    match software_method:
        case 1 | 3:
            while True:
                try:
                    await Reger(private_key=private_key).start_reger(proxy=proxy)

                except Exception as error:
                    logger.error(f'Unexpected Error: {error}')

                else:
                    return

        case 2:
            while True:
                try:
                    await Reger().start_reger(proxy=next(proxies_cycled) if proxies_cycled else None)

                except Exception as error:
                    logger.error(f'Unexpected Error: {error}')

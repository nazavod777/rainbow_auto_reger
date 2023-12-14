from random import choice

import aiofiles


async def get_ref_code() -> str:
    async with aiofiles.open(file='ref_codes.txt',
                             mode='r',
                             encoding='utf-8-sig') as file:
        ref_codes: list[str] = [row.strip() for row in await file.readlines()]

    return choice(ref_codes)

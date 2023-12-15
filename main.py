import asyncio
from itertools import cycle
from os.path import exists

from better_proxy import Proxy

from core import start_reger
from utils import logger


async def main() -> None:
    match software_method:
        case 1:
            tasks: list = [start_reger(software_method=software_method,
                                       proxy=next(proxies_cycled) if proxies_list else None)
                           for _ in range(len(proxies_list))]

        case 2:
            tasks: list = [start_reger(software_method=software_method,
                                       proxies_cycled=proxies_cycled) for _ in range(threads)]

        case 3:
            tasks: list = [start_reger(software_method=software_method,
                                       proxies_cycled=proxies_cycled,
                                       private_key=current_private_key) for current_private_key in accounts_list]

        case _:
            return

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    if exists(path='proxies.txt'):
        proxies_list: list[str] = [proxy.as_url for proxy in Proxy.from_file(filepath='proxies.txt')]

    else:
        proxies_list: list[str] = []

    if exists(path='accounts.txt'):
        with open(file='accounts.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            accounts_list: list[str] = [row.strip() if row.strip().startswith('0x')
                                        else f'0x{row.strip()}' for row in file]

    else:
        accounts_list: list[str] = []

    proxies_cycled: cycle | None = cycle(proxies_list) if proxies_list else None

    logger.success(f'Successfully loaded {len(accounts_list)} accounts | {len(proxies_list)} proxies')

    threads: int = int(input('\nThreads: '))
    software_method: int = int(input('\n1. Register 1 account per 1 proxy\n'
                                     '2. Infinity register\n'
                                     '3. Register with private keys\n'
                                     'Choose: '))
    print()

    asyncio.run(main())

    logger.success('Work Has Been Successfully Finished')
    input('\nPress Enter to Exit..')

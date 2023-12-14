from aiohttp_proxy import ProxyConnector


async def get_connector(proxy: str | None) -> ProxyConnector | None:
    if not proxy:
        return None

    return ProxyConnector.from_url(url=proxy)

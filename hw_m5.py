import sys
from datetime import datetime, timedelta

import aiohttp
import asyncio
import platform


class HttpError(Exception):
    pass


class PrivatBankAPI:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?date={date}"

    @staticmethod
    async def fetch_exchange_rates(date: str):
        url = PrivatBankAPI.BASE_URL.format(date=date)
        async with aiohttp.ClientSession() as session:
            try:
                responce = await session.get(url)
                if responce.status == 200:
                    result = await responce.json()
                    return result
                else:
                    raise HttpError(f"Error status: {responce.status} for {url}")
            except (aiohttp.ClientConnectionError, aiohttp.InvalidURL) as err:
                raise HttpError(f"Connection error: {url}: {err}")


async def get_exchange_rates(index_day: int):
    if index_day < 0 or index_day > 10:
        raise ValueError("Index day must be between 0 and 10.")

    date = (datetime.now() - timedelta(days=index_day)).strftime("%d.%m.%Y")
    try:
        data = await PrivatBankAPI.fetch_exchange_rates(date)
        rates = {}
        if "exchangeRate" in data:
            for rate in data["exchangeRate"]:
                if rate["currency"] in ["USD", "EUR"]:
                    rates[rate["currency"]] = {
                        "sale": rate.get("saleRate"),
                        "purchase": rate.get("purchaseRate")
                    }
        return {date: rates} if rates else None
    except HttpError as err:
        print(err)
        return None


async def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: hw_m5.py <days>")
        return

    index_day = int(sys.argv[1])
    result = await get_exchange_rates(index_day)
    if result:
        print(result)
    else:
        print("No data found for the specified date.")


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())

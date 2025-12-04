import asyncio
from app.services.scraper import scrape_page

async def run():
    text = await scrape_page("https://www.asynk.in/")
    print(text[:500])  # print first 500 chars

asyncio.run(run())

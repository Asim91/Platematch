from fastapi import APIRouter, HTTPException
import httpx
from bs4 import BeautifulSoup

router = APIRouter()

@router.get("/scrape/{auction_id}")
async def scrape_auction_data(auction_id: str):
    url = f"https://dvlaauction.co.uk/auction/{auction_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            auction_data = []

            for record in soup.select('tr.record.record-lot'):
                lot_number = record.select_one('.field-id').text.strip()
                registration = record.select_one('.field-name.data-text')['data-search']
                reserve_price = record.select_one('.field-reserve.data-gbp').text.strip()
                current_price = record.select_one('.field-current-price.data-gbp').text.strip()
                end_time = record.select_one('.field-end-time.data-datetime').text.strip()
                lot_url = record.select_one('.field-lot-url').text.strip()

                auction_data.append({
                    "lotNumber": lot_number,
                    "registration": registration,
                    "reservePrice": reserve_price,
                    "currentPrice": current_price,
                    "endTime": end_time,
                    "lotUrl": lot_url,
                })

            return auction_data
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
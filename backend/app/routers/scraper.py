from fastapi import APIRouter, HTTPException
from app.schemas.recipe import ScrapeRequest, ScrapeResponse
from app.services.scraper_service import scrape_recipe

router = APIRouter()


@router.post("/", response_model=ScrapeResponse)
async def scrape(data: ScrapeRequest):
    try:
        result = await scrape_recipe(data.url)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
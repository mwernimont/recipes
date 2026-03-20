import httpx
import json
import re
from bs4 import BeautifulSoup
from app.schemas.recipe import ScrapeResponse, IngredientCreate, StepCreate


def parse_duration(duration: str | None) -> int | None:
    """Convert ISO 8601 duration (PT1H30M) to minutes."""
    if not duration:
        return None
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    total = 0
    if hours:
        total += int(hours.group(1)) * 60
    if minutes:
        total += int(minutes.group(1))
    return total if total > 0 else None


def parse_servings(servings_raw: str | None) -> float | None:
    """Extract a float from servings strings like '4', '4 servings', 'serves 4'."""
    if not servings_raw:
        return None
    match = re.search(r'(\d+\.?\d*)', str(servings_raw))
    return float(match.group(1)) if match else None


def parse_ingredient(raw: str) -> IngredientCreate:
    """
    Best-effort parse of an ingredient string into amount, unit, name.
    Falls back to storing the full string as name if parsing fails.
    """
    raw = raw.strip()

    amount_pattern = r'^(\d+\.?\d*|\d+/\d+)\s*'
    units = [
        'cup', 'cups', 'tbsp', 'tsp', 'tablespoon', 'tablespoons',
        'teaspoon', 'teaspoons', 'oz', 'ounce', 'ounces', 'lb', 'lbs',
        'pound', 'pounds', 'g', 'gram', 'grams', 'kg', 'ml', 'liter',
        'liters', 'l', 'pinch', 'pinches', 'clove', 'cloves', 'slice',
        'slices', 'piece', 'pieces', 'can', 'cans', 'bunch', 'bunches',
    ]
    unit_pattern = r'(' + '|'.join(units) + r')\s*'

    amount = None
    unit = None
    name = raw

    amount_match = re.match(amount_pattern, raw, re.IGNORECASE)
    if amount_match:
        raw_amount = amount_match.group(1)
        # handle fractions like 1/2
        if '/' in raw_amount:
            num, denom = raw_amount.split('/')
            amount = float(num) / float(denom)
        else:
            amount = float(raw_amount)

        remainder = raw[amount_match.end():]
        unit_match = re.match(unit_pattern, remainder, re.IGNORECASE)
        if unit_match:
            unit = unit_match.group(1).lower()
            name = remainder[unit_match.end():].strip()
        else:
            name = remainder.strip()

    return IngredientCreate(amount=amount, unit=unit, name=name or raw)


def parse_schema_org(data: dict) -> ScrapeResponse | None:
    """Parse a schema.org Recipe JSON-LD object into a ScrapeResponse."""
    if not data.get("@type") == "Recipe":
        return None

    # Parse ingredients
    raw_ingredients = data.get("recipeIngredient", [])
    ingredients = [parse_ingredient(i) for i in raw_ingredients]

    # Parse steps
    raw_instructions = data.get("recipeInstructions", [])
    steps = []
    for i, step in enumerate(raw_instructions):
        if isinstance(step, dict):
            text = step.get("text", "")
        else:
            text = str(step)
        if text.strip():
            steps.append(StepCreate(order=i + 1, instruction=text.strip()))

    # Parse servings
    servings_raw = data.get("recipeYield")
    if isinstance(servings_raw, list):
        servings_raw = servings_raw[0] if servings_raw else None

    return ScrapeResponse(
        title=data.get("name", "Untitled Recipe"),
        description=data.get("description"),
        source_url=data.get("url", ""),
        prep_time_minutes=parse_duration(data.get("prepTime")),
        cook_time_minutes=parse_duration(data.get("cookTime")),
        servings=parse_servings(servings_raw),
        ingredients=ingredients,
        steps=steps,
    )


async def scrape_recipe(url: str) -> ScrapeResponse:
    """Fetch a URL and attempt to extract recipe data via schema.org JSON-LD."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for JSON-LD script tags
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)

            # Handle @graph arrays
            if isinstance(data, dict) and "@graph" in data:
                for item in data["@graph"]:
                    if item.get("@type") == "Recipe":
                        result = parse_schema_org(item)
                        if result:
                            result.source_url = url
                            return result

            # Handle direct Recipe object
            if isinstance(data, dict) and data.get("@type") == "Recipe":
                result = parse_schema_org(data)
                if result:
                    result.source_url = url
                    return result

            # Handle arrays of objects
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Recipe":
                        result = parse_schema_org(item)
                        if result:
                            result.source_url = url
                            return result

        except (json.JSONDecodeError, Exception):
            continue

    raise ValueError(f"No schema.org Recipe data found at {url}")
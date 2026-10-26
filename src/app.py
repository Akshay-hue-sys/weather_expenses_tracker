from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from projects.weather_expense_tracker.src.database import (
    get_expense_summary,
    init_db,
    insert_expense,
    list_expenses,
)
from projects.weather_expense_tracker.src.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseSummary,
    WeatherInfo,
)
from projects.weather_expense_tracker.src.weather import (
    fetch_current_weather,
    search_weather_by_name,
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Weather & Expense Tracker API",
    description="Independent dual-service API: Live Weather Lookup & SQLite Expense Tracker",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/weather", response_model=WeatherInfo, tags=["Weather Service"])
async def get_weather(
    latitude: float = Query(ge=-90.0, le=90.0, description="Latitude in degrees"),
    longitude: float = Query(ge=-180.0, le=180.0, description="Longitude in degrees"),
) -> WeatherInfo:
    weather = await fetch_current_weather(latitude=latitude, longitude=longitude)
    if weather is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="External weather service is currently unreachable.",
        )
    return weather


@app.get("/weather/search", tags=["Weather Service"])
async def search_weather(
    location_name: str = Query(min_length=1, max_length=100, description="City, state, or country name"),
) -> dict:
    result = await search_weather_by_name(query=location_name)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location '{location_name}' could not be found or weather is unavailable.",
        )
    return result


@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Expense Tracker"],
)
async def create_expense(expense: ExpenseCreate) -> ExpenseResponse:
    saved_record = insert_expense(expense=expense)
    return ExpenseResponse(**saved_record)


@app.get("/expenses", response_model=list[ExpenseResponse], tags=["Expense Tracker"])
async def get_all_expenses() -> list[ExpenseResponse]:
    records = list_expenses()
    return [ExpenseResponse(**rec) for rec in records]


@app.get("/expenses/summary", response_model=ExpenseSummary, tags=["Expense Tracker"])
async def get_summary() -> ExpenseSummary:
    summary_data = get_expense_summary()
    return ExpenseSummary(**summary_data)


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
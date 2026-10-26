from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class WeatherInfo(BaseModel):
    temperature_c: float
    weather_code: int
    wind_speed_kmh: float


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0.0)
    category: str = Field(min_length=1, max_length=50)

    @field_validator("title", "category")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return cleaned


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    created_at: datetime


class ExpenseSummary(BaseModel):
    total_amount: float
    expense_count: int
    category_totals: dict[str, float]
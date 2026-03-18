from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Global Healthcare API",
    description="Global healthcare data including life expectancy, health spending, doctor density, hospital beds, and health rankings for 190+ countries. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "life_expectancy":   {"id": "SP.DYN.LE00.IN",    "name": "Life Expectancy at Birth",          "unit": "Years"},
    "health_spending":   {"id": "SH.XPD.CHEX.GD.ZS", "name": "Current Health Expenditure",        "unit": "% of GDP"},
    "health_spend_pc":   {"id": "SH.XPD.CHEX.PC.CD", "name": "Health Expenditure Per Capita",     "unit": "Current USD"},
    "physicians":        {"id": "SH.MED.PHYS.ZS",    "name": "Physicians Density",                "unit": "Per 1,000 People"},
    "hospital_beds":     {"id": "SH.MED.BEDS.ZS",    "name": "Hospital Beds",                     "unit": "Per 1,000 People"},
    "infant_mortality":  {"id": "SP.DYN.IMRT.IN",    "name": "Infant Mortality Rate",             "unit": "Per 1,000 Live Births"},
    "maternal_mortality":{"id": "SH.STA.MMRT",       "name": "Maternal Mortality Ratio",          "unit": "Per 100,000 Live Births"},
    "immunization_dpt":  {"id": "SH.IMM.IDPT",       "name": "DPT Immunization Rate",             "unit": "% of Children 12-23 Months"},
    "nurses":            {"id": "SH.MED.NUMW.P3",    "name": "Nurses and Midwives",               "unit": "Per 1,000 People"},
}

COUNTRIES = {
    "WLD": "World",
    "USA": "United States",
    "CHN": "China",
    "DEU": "Germany",
    "JPN": "Japan",
    "GBR": "United Kingdom",
    "FRA": "France",
    "KOR": "South Korea",
    "CHE": "Switzerland",
    "AUS": "Australia",
    "CAN": "Canada",
    "NOR": "Norway",
    "SWE": "Sweden",
    "FIN": "Finland",
    "NLD": "Netherlands",
    "IND": "India",
    "BRA": "Brazil",
    "RUS": "Russia",
    "ZAF": "South Africa",
    "NGA": "Nigeria",
    "ETH": "Ethiopia",
    "BGD": "Bangladesh",
    "PAK": "Pakistan",
    "IDN": "Indonesia",
    "MEX": "Mexico",
    "TUR": "Turkey",
    "ITA": "Italy",
    "ESP": "Spain",
    "POL": "Poland",
    "SGP": "Singapore",
}


async def fetch_wb_country(country_code: str, indicator_id: str, limit: int = 10):
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


async def fetch_wb_all_countries(indicator_id: str):
    url = f"{WB_BASE}/country/all/indicator/{indicator_id}"
    params = {"format": "json", "mrv": 1, "per_page": 300}
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"country_code": r["countryiso3code"], "country": r["country"]["value"], "year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None and r.get("countryiso3code")
    ]


@app.get("/")
def root():
    return {
        "api": "Global Healthcare API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "endpoints": [
            "/summary", "/life-expectancy", "/spending", "/physicians",
            "/hospital-beds", "/infant-mortality", "/maternal-mortality",
            "/immunization", "/life-expectancy-ranking", "/spending-ranking"
        ],
        "countries": list(COUNTRIES.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=5, ge=1, le=30)
):
    """All healthcare indicators for a country"""
    country = country.upper()
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb_country(country, meta["id"], limit)
    formatted = {
        key: {"name": INDICATORS[key]["name"], "unit": INDICATORS[key]["unit"], "data": results[key]}
        for key in INDICATORS
    }
    return {"country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank Open Data", "updated_at": datetime.utcnow().isoformat() + "Z", "indicators": formatted}


@app.get("/life-expectancy")
async def life_expectancy(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Life expectancy at birth (years)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.DYN.LE00.IN", limit)
    return {"indicator": "Life Expectancy at Birth", "series_id": "SP.DYN.LE00.IN", "unit": "Years", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/spending")
async def spending(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Current health expenditure (% of GDP and per capita USD)"""
    country = country.upper()
    pct_gdp = await fetch_wb_country(country, "SH.XPD.CHEX.GD.ZS", limit)
    per_cap = await fetch_wb_country(country, "SH.XPD.CHEX.PC.CD", limit)
    return {
        "country_code": country, "country": COUNTRIES.get(country, country),
        "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z",
        "pct_gdp": {"series_id": "SH.XPD.CHEX.GD.ZS", "unit": "% of GDP", "data": pct_gdp},
        "per_capita": {"series_id": "SH.XPD.CHEX.PC.CD", "unit": "Current USD", "data": per_cap},
    }


@app.get("/physicians")
async def physicians(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Physicians density (per 1,000 people)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SH.MED.PHYS.ZS", limit)
    return {"indicator": "Physicians Density", "series_id": "SH.MED.PHYS.ZS", "unit": "Per 1,000 People", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/hospital-beds")
async def hospital_beds(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Hospital beds per 1,000 people"""
    country = country.upper()
    data = await fetch_wb_country(country, "SH.MED.BEDS.ZS", limit)
    return {"indicator": "Hospital Beds", "series_id": "SH.MED.BEDS.ZS", "unit": "Per 1,000 People", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/infant-mortality")
async def infant_mortality(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Infant mortality rate (per 1,000 live births)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SP.DYN.IMRT.IN", limit)
    return {"indicator": "Infant Mortality Rate", "series_id": "SP.DYN.IMRT.IN", "unit": "Per 1,000 Live Births", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/maternal-mortality")
async def maternal_mortality(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Maternal mortality ratio (per 100,000 live births)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SH.STA.MMRT", limit)
    return {"indicator": "Maternal Mortality Ratio", "series_id": "SH.STA.MMRT", "unit": "Per 100,000 Live Births", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/immunization")
async def immunization(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """DPT immunization rate among children ages 12-23 months (%)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SH.IMM.IDPT", limit)
    return {"indicator": "DPT Immunization Rate", "series_id": "SH.IMM.IDPT", "unit": "% of Children 12-23 Months", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/life-expectancy-ranking")
async def life_expectancy_ranking(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by life expectancy at birth"""
    data = await fetch_wb_all_countries("SP.DYN.LE00.IN")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {"indicator": "Life Expectancy at Birth", "unit": "Years", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "life_expectancy_ranking": ranked}


@app.get("/spending-ranking")
async def spending_ranking(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by health expenditure as % of GDP"""
    data = await fetch_wb_all_countries("SH.XPD.CHEX.GD.ZS")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {"indicator": "Health Expenditure", "unit": "% of GDP", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "spending_ranking": ranked}

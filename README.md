# Global Healthcare API

Global healthcare data including life expectancy, health spending, physician density, hospital beds, infant mortality, maternal mortality, and immunization rates for 190+ countries. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All healthcare indicators for a country |
| `GET /life-expectancy` | Life expectancy at birth (years) |
| `GET /spending` | Health expenditure (% of GDP & per capita) |
| `GET /physicians` | Physician density (per 1,000 people) |
| `GET /hospital-beds` | Hospital beds (per 1,000 people) |
| `GET /infant-mortality` | Infant mortality rate |
| `GET /maternal-mortality` | Maternal mortality ratio |
| `GET /immunization` | DPT immunization rate |
| `GET /life-expectancy-ranking` | Countries ranked by life expectancy |
| `GET /spending-ranking` | Countries ranked by health spending |

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `country` | ISO3 country code (e.g., USA, JPN, NOR) | `WLD` |
| `limit` | Number of years or countries | `10` |

## Data Source

World Bank Open Data
https://data.worldbank.org/indicator/SP.DYN.LE00.IN

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.

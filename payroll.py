from config import REVENUE_PERCENT, SHOP_RATES


def calculate_salary(shop: str, revenue: float, fine: float) -> dict[str, float]:
    revenue = max(0.0, float(revenue))
    fine = max(0.0, float(fine))
    base = float(SHOP_RATES[shop])
    percent = round(revenue * REVENUE_PERCENT, 2)
    total = round(base + percent - fine, 2)
    return {
        "base": base,
        "percent": percent,
        "fine": fine,
        "total": total,
    }


def format_rubles(amount: float) -> str:
    return f"{amount:,.0f} ₽"


def percent_share_of_total(result: dict[str, float]) -> float | None:
    total = result["total"]
    if total <= 0:
        return None
    return min(result["percent"] / total, 1.0)

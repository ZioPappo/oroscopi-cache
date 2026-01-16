import os, json
from datetime import datetime
import pytz
import swisseph as swe

TZ = pytz.timezone("Europe/Rome")

SIGNS = ["Ariete","Toro","Gemelli","Cancro","Leone","Vergine","Bilancia","Scorpione","Sagittario","Capricorno","Acquario","Pesci"]

PLANETS = {
    "Sole": swe.SUN,
    "Luna": swe.MOON,
    "Mercurio": swe.MERCURY,
    "Venere": swe.VENUS,
    "Marte": swe.MARS,
    "Giove": swe.JUPITER,
    "Saturno": swe.SATURN,
    "Urano": swe.URANUS,
    "Nettuno": swe.NEPTUNE,
    "Plutone": swe.PLUTO,
}

def zodiac_sign(lon_deg: float) -> str:
    i = int(lon_deg // 30) % 12
    return SIGNS[i]

def iso_week_id(dt: datetime) -> str:
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def main():
    now = datetime.now(TZ)
    ymd = now.strftime("%Y-%m-%d")
    ym  = now.strftime("%Y-%m")
    week = iso_week_id(now)

    out_daily = f"output/daily/daily_{ymd}.json"
    out_week  = f"output/weekly/weekly_{week}.json"
    out_month = f"output/monthly/monthly_{ym}.json"

    # Non sovrascrivere mai: immutabile
    if os.path.exists(out_daily) and os.path.exists(out_week) and os.path.exists(out_month):
        print("File del periodo già presenti. Esco.")
        return

    # Calcolo posizioni a mezzogiorno locale
    dt = datetime(now.year, now.month, now.day, 12, 0, 0, tzinfo=TZ)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

    planets = {}
    for name, pid in PLANETS.items():
        lon, lat, dist = swe.calc_ut(jd, pid)[0][:3]
        planets[name] = {
            "lon": round(lon, 4),
            "sign": zodiac_sign(lon),
        }

    base = {
        "generated_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "date_ref": ymd,
        "planets": planets,
        "note": "Dati astronomici calcolati con Swiss Ephemeris (pyswisseph)."
    }

    ensure_dir("output/daily")
    ensure_dir("output/weekly")
    ensure_dir("output/monthly")

    if not os.path.exists(out_daily):
        with open(out_daily, "w", encoding="utf-8") as f:
            json.dump({**base, "type": "daily", "id": ymd}, f, ensure_ascii=False, indent=2)

    if not os.path.exists(out_week):
        with open(out_week, "w", encoding="utf-8") as f:
            json.dump({**base, "type": "weekly", "id": week}, f, ensure_ascii=False, indent=2)

    if not os.path.exists(out_month):
        with open(out_month, "w", encoding="utf-8") as f:
            json.dump({**base, "type": "monthly", "id": ym}, f, ensure_ascii=False, indent=2)

    print("OK: file generati (se mancanti).")

if __name__ == "__main__":
    main()

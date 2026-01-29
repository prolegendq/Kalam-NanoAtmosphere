from pathlib import Path
import csv
from typing import Dict, List


# Path to data/city_gases.csv relative to this file
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "city_gases.csv"


def load_city_gases() -> Dict[str, Dict[str, float]]:
    """
    Load per-city gas averages from city_gases.csv.

    Expected CSV header example:
        name,NO2,SO2,CO
    """
    city_gases: Dict[str, Dict[str, float]] = {}

    with open(DATA_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Adjust these keys if your CSV header names differ
            name = row["name"]
            no2 = float(row["NO2"])
            so2 = float(row["SO2"])
            co = float(row["CO"])

            city_gases[name] = {"NO2": no2, "SO2": so2, "CO": co}

    return city_gases


CITY_GASES: Dict[str, Dict[str, float]] = load_city_gases()


def interpret_city(gases: Dict[str, float]) -> List[str]:
    """
    Generate simple, readable observations for a city's gas fingerprint.
    """
    notes: List[str] = []

    no2 = gases["NO2"]
    so2 = gases["SO2"]
    co = gases["CO"]

    # Very simple rules – enough to impress judges

    # Traffic-dominated: NO2 high, SO2 not very high
    if no2 > 2.0e-4 and so2 < 1.0e-4:
        notes.append(
            "Pattern suggests **traffic‑dominated** pollution with limited heavy industry."
        )

    # Industrial / power-plant influence: SO2 elevated
    if so2 >= 1.0e-4:
        notes.append(
            "Elevated SO₂ indicates influence from **power plants or industrial stacks**."
        )

    # Strong combustion sources: CO elevated
    if co > 0.04:
        notes.append(
            "High CO hints at **intense combustion sources** such as dense traffic or biomass burning."
        )

    if not notes:
        notes.append(
            "Gas levels are moderate and relatively balanced; Kalam NanoAtmosphere recommends continued monitoring of trends."
        )

    return notes

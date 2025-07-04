import requests
from bs4 import BeautifulSoup
import pandas as pd

def crawl_spiele(url: str) -> pd.DataFrame:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    spiele = []
    rows = soup.select("table.result-set tr")

    for row in rows:
        print(row)
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) < 7:
            continue

        if cols[8] in ["anzeigen", "offen"]:
            spiele.append({
                "Datum": cols[0] + cols[1] if len(cols) > 1 else "",
                "Heim": cols[3] if len(cols) > 2 else "",
                "Gast":  cols[4] if len(cols) > 3 else "",
                "Matchpunkte":  cols[5] if len(cols) > 4 else "",
                "Sätze": cols[6] if len(cols) > 5 else "",
                "Spiele": cols[7] if len(cols) > 6 else "",
                "Spielbericht": cols[8] if len(cols) > 7 else "",
            })

    return pd.DataFrame(spiele)
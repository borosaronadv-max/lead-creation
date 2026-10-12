"""Telefonkönyv ↔ LinkedIn-kapcsolatok egyeztetése.

Használat:
    python3 scripts/telefonkonyv_egyeztetes.py Connections.csv telefonkonyv.(csv|vcf) [--napló data/linkedin-meghivo-naplo.csv] [--max 20]

Kimenet (stdout, CSV): azok a telefonkönyv-bejegyzések, akik nincsenek a
LinkedIn-kapcsolatok között, LinkedIn-keresőlinkkel.
"""
import argparse
import csv
import io
import re
import sys
import unicodedata
import urllib.parse

TITULUSOK = {"dr", "ifj", "id", "prof", "phd", "mba", "jr", "sr", "dipl", "ing"}


def nev_kulcs(nev):
    """Ékezet, titulus és sorrend nélküli névkulcs (Kovács Péter == Peter Kovacs)."""
    nev = unicodedata.normalize("NFKD", nev or "")
    nev = "".join(c for c in nev if not unicodedata.combining(c)).lower()
    szavak = [s for s in re.split(r"[^a-z]+", nev) if s and s not in TITULUSOK]
    return " ".join(sorted(szavak))


def kapcsolatok_beolvasasa(utvonal):
    with open(utvonal, encoding="utf-8-sig") as f:
        sorok = f.read().splitlines()
    fejlec = next(i for i, s in enumerate(sorok) if s.startswith("First Name,"))
    olvaso = csv.DictReader(io.StringIO("\n".join(sorok[fejlec:])))
    nevek, emailek = set(), set()
    for r in olvaso:
        nevek.add(nev_kulcs(f"{r['First Name']} {r['Last Name']}"))
        if r.get("Email Address"):
            emailek.add(r["Email Address"].strip().lower())
    return nevek, emailek


def vcf_beolvasasa(szoveg):
    for kartya in re.split(r"(?im)^BEGIN:VCARD", szoveg)[1:]:
        kartya = re.sub(r"\r?\n[ \t]", "", kartya)  # összehajtott sorok
        mezo = lambda kulcs: [
            m.group(1).strip() for m in re.finditer(rf"(?im)^{kulcs}[^:\n]*:(.*)$", kartya)
        ]
        nev = (mezo("FN") or [""])[0]
        if not nev and mezo("N"):
            vezetek, kereszt, *_ = (mezo("N")[0] + ";;").split(";")
            nev = f"{vezetek} {kereszt}".strip()
        yield {
            "nev": nev,
            "ceg": (mezo("ORG") or [""])[0].split(";")[0],
            "email": (mezo("EMAIL") or [""])[0],
            "telefon": (mezo("TEL") or [""])[0],
        }


def csv_beolvasasa(szoveg):
    """Google Contacts / Outlook CSV-export."""
    for r in csv.DictReader(io.StringIO(szoveg)):
        nev = r.get("Name") or " ".join(
            filter(None, [r.get("First Name") or r.get("Given Name"), r.get("Middle Name"),
                          r.get("Last Name") or r.get("Family Name")])
        )
        yield {
            "nev": nev.strip(),
            "ceg": r.get("Organization Name") or r.get("Organization 1 - Name") or r.get("Company") or "",
            "email": r.get("E-mail 1 - Value") or r.get("E-mail Address") or r.get("Email") or "",
            "telefon": r.get("Phone 1 - Value") or r.get("Mobile Phone") or r.get("Phone") or "",
        }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kapcsolatok")
    p.add_argument("telefonkonyv")
    p.add_argument("--naplo", help="korábban listázottak (nev oszlop), ezeket kihagyja")
    p.add_argument("--max", type=int, default=20)
    a = p.parse_args()

    nevek, emailek = kapcsolatok_beolvasasa(a.kapcsolatok)
    with open(a.telefonkonyv, encoding="utf-8-sig", errors="replace") as f:
        szoveg = f.read()
    bejegyzesek = vcf_beolvasasa(szoveg) if "BEGIN:VCARD" in szoveg[:2000] else csv_beolvasasa(szoveg)

    kihagy = set()
    if a.naplo:
        try:
            with open(a.naplo, encoding="utf-8") as f:
                kihagy = {nev_kulcs(r["nev"]) for r in csv.DictReader(f)}
        except FileNotFoundError:
            pass

    latott, talalatok = set(), []
    for b in bejegyzesek:
        kulcs = nev_kulcs(b["nev"])
        # Egyszavas nevek (pl. "Anyu", "Vízvezeték-szerelő") nem azonosíthatók.
        if len(kulcs.split()) < 2 or kulcs in latott or kulcs in kihagy:
            continue
        latott.add(kulcs)
        if kulcs in nevek or (b["email"] and b["email"].lower() in emailek):
            continue
        kereses = urllib.parse.quote_plus(f"{b['nev']} {b['ceg']}".strip())
        b["kereso_link"] = f"https://www.linkedin.com/search/results/people/?keywords={kereses}"
        talalatok.append(b)

    # Előre azok, akiknél van cég (pontosabb keresés, valószínűbb szakmai kapcsolat).
    talalatok.sort(key=lambda b: (not b["ceg"], b["nev"]))
    w = csv.DictWriter(sys.stdout, fieldnames=["nev", "ceg", "email", "telefon", "kereso_link"])
    w.writeheader()
    w.writerows(talalatok[: a.max])
    print(f"# telefonkönyv: {len(latott)} egyedi név, nincs LinkedIn-kapcsolat: {len(talalatok)}", file=sys.stderr)


if __name__ == "__main__":
    main()

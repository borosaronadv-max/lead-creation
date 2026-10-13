"""Telefonkönyv ↔ LinkedIn-kapcsolatok egyeztetése.

Használat:
    python3 scripts/telefonkonyv_egyeztetes.py Connections.csv telefonkonyv.(csv|vcf|xlsx)
        [--lap Kontaktok_Tisztitott] [--prioritas lp_final_score]
        [--celcsoport] [--naplo data/linkedin-meghivo-naplo.csv] [--kapcsolat "Név" ...] [--max 20]

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

TITULUSOK = {"dr", "ifj", "id", "prof", "phd", "mba", "jr", "sr", "dipl", "ing", "mr", "mrs", "ms", "mrics", "architect", "msc"}


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


def xlsx_beolvasasa(utvonal, lap):
    """Outlook-stílusú oszlopnevek (display_name, organization, ...) xlsx-ben."""
    import openpyxl

    wb = openpyxl.load_workbook(utvonal, read_only=True, data_only=True)
    ws = wb[lap] if lap else wb.worksheets[0]
    sorok = ws.iter_rows(values_only=True)
    fejlec = [str(c or "").strip().lower() for c in next(sorok)]
    for sor in sorok:
        r = {k: ("" if v is None else str(v).strip()) for k, v in zip(fejlec, sor)}
        nev = r.get("display_name") or f"{r.get('last_name', '')} {r.get('first_name', '')}".strip()
        yield {
            "nev": nev,
            "ceg": r.get("organization", ""),
            "beosztas": r.get("job_title", ""),
            "email": r.get("e-mail_address", ""),
            "telefon": r.get("mobile_phone") or r.get("business_phone", ""),
            "_sor": r,
        }


# Célcsoport: 2–20 Mrd Ft árbevételű cégek tulajdonosai, CEO-i, CFO-i.
# A pozíciót a beosztásból ismeri fel; az árbevételt a névjegyek nem tartalmazzák,
# ezért a szervezetek közül csak a biztosan nem célcsoportba tartozókat zárja ki
# (bank, állam, oktatás, egyesület, nagyvállalat, Big4). Az árbevételt a böngészős
# lépés ellenőrzi.
SZEREPEK = [
    ("tulajdonos", r"tulajdonos|owner|alapito|founder|managing partner|\bpartner\b|reszvenyes|shareholder"),
    ("CEO", r"\bceo\b|vezerigazgato|ugyvezet|managing director|general manager|chief executive"
            r"|\bmd\b|geschaftsfuhrer|igazgatosag elnoke"),
    ("CFO", r"\bcfo\b|penzugyi igazgato|gazdasagi igazgato|finance director|financial director"
            r"|chief financial|penzugyi vezeto|gazdasagi vezeto"),
]
NEM_SZEREP = (r"helyettes|deputy|assistant|asszisztens|titkar|\bvice\b|\bvp\b|alelnok"
              r"|advisor to|to the ceo|of the ceo|office of")
NEM_CELCEG = (
    r"\bbank|bankholding|takarek|\bmkb\b|\bmnb\b|central bank|nemzeti bank|miniszter|ministry"
    r"|kormany|hivatal|onkormanyzat|egyetem|university|foiskola|iskola|kamara|szovetseg"
    r"|association|egyesulet|alapitvany|foundation|biztosito|insurance|nonprofit|non-profit"
    r"|npkft|\bkht\b|allami|\bstate\b|ebrd|european bank|\bexim|\bmfb\b|\botp\b|\bmol\b"
    r"|telekom|richter|\b4ig\b|\bmvm\b|magyar posta|\bmav\b|volan|fovaros|rendorseg|kozmu"
    r"|\bnkm\b|\bbkv\b|\bbdo\b|kpmg|deloitte|ernst|\bey\b|pwc|grant thornton|siemens|\bibm\b"
    r"|microsoft|oracle|\bsap\b|ericsson|nokia|vodafone|yettel|\baudi\b|mercedes|bosch"
    r"|samsung|tesco|spar\b|auchan|lidl|aldi|klaszter|cluster|\belte\b|\bbme\b|\bkar\b"
    # alapkezelők, befektetők (árbevételük jellemzően 2 Mrd Ft alatti, más célcsoport)
    r"|alapkezelo|befektetesi|\bcapital\b|private equity|tokealap|\binvest\b|\bpromid\b"
    # ismerten 20 Mrd Ft fölötti cégcsoportok
    r"|beres|\bcba\b|\begis\b|centrica|richter|waberer|zwack|pick szeged|bonafarm"
)


def ekezet_nelkul(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def celcsoport_szerep(beosztas, ceg):
    """'tulajdonos' / 'CEO' / 'CFO', ha a névjegy a célcsoportba eshet, különben None."""
    b, c = ekezet_nelkul(beosztas), ekezet_nelkul(ceg)
    if not b or not c or re.search(NEM_SZEREP, b) or re.search(NEM_CELCEG, c):
        return None
    for szerep, minta in SZEREPEK:
        if re.search(minta, b):
            return szerep
    return None


def nev_tisztitas(nev):
    """Megjelenítési név a névjegy-zajtól (titulus, végzettség, "RT HUNGARY") megtisztítva."""
    szavak = [sz for sz in nev.split()
              if sz.lower().strip(".,") not in TITULUSOK and "." not in sz and not sz.islower()]
    if len(szavak) > 3:
        szavak = [sz for sz in szavak if not sz.isupper()] or szavak
    # ismétlődő szó ("Balog Balog Ádám")
    tiszta = [sz for i, sz in enumerate(szavak) if i == 0 or sz != szavak[i - 1]]
    return " ".join(tiszta) or nev


def szam(ertek):
    try:
        return float(ertek)
    except (TypeError, ValueError):
        return 0.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kapcsolatok")
    p.add_argument("telefonkonyv")
    p.add_argument("--naplo", help="korábban listázottak (nev oszlop), ezeket kihagyja")
    p.add_argument("--max", type=int, default=20)
    p.add_argument("--lap", help="xlsx munkalap neve (alapból az első)")
    p.add_argument("--prioritas", help="xlsx oszlop, ami szerint csökkenő sorrendbe rendez")
    p.add_argument("--celcsoport", action="store_true",
                   help="csak tulajdonos/CEO/CFO, nem bank/állam/nagyvállalat (2–20 Mrd Ft cél)")
    p.add_argument("--kapcsolat", nargs="*", default=[],
                   help="az export óta elfogadott meghívók nevei (kapcsolatnak számítanak)")
    a = p.parse_args()

    nevek, emailek = kapcsolatok_beolvasasa(a.kapcsolatok)
    nevek |= {nev_kulcs(n) for n in a.kapcsolat}
    if a.telefonkonyv.lower().endswith((".xlsx", ".xlsm")):
        bejegyzesek = xlsx_beolvasasa(a.telefonkonyv, a.lap)
    else:
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

    latott, talalatok, egyezett = set(), [], 0
    for b in bejegyzesek:
        kulcs = nev_kulcs(b["nev"])
        # Egyszavas nevek (pl. "Anyu", "Vízvezeték-szerelő") nem azonosíthatók.
        if len(kulcs.split()) < 2 or kulcs in latott or kulcs in kihagy:
            continue
        latott.add(kulcs)
        if a.celcsoport:
            b["szerep"] = celcsoport_szerep(b.get("beosztas", ""), b["ceg"])
            if not b["szerep"]:
                continue
        if kulcs in nevek or (b["email"] and b["email"].lower() in emailek):
            egyezett += 1
            continue
        b["prioritas"] = (b.get("_sor") or {}).get(a.prioritas.lower(), "") if a.prioritas else ""
        ceg_rovid = " ".join(re.sub(r"[^\w\s&.-]", " ", b["ceg"]).split()[:2])
        tiszta_nev = nev_tisztitas(b["nev"])
        b["nev_tiszta"] = tiszta_nev
        kereses = urllib.parse.quote_plus(f"{tiszta_nev} {ceg_rovid}".strip())
        b["kereso_link"] = f"https://www.linkedin.com/search/results/people/?keywords={kereses}"
        talalatok.append(b)

    # A három célcsoport-szerep egyenrangú; előbb a prioritás, aztán akinél van cég.
    szerep_sorrend = {"tulajdonos": 0, "CEO": 0, "CFO": 0}
    # A Zrt. forma a 2–20 Mrd Ft-os sávban gyakoribb, mint a kis Kft.-knél.
    zrt = lambda b: 0 if re.search(r"\bzrt\b|\brt\b", ekezet_nelkul(b["ceg"])) else 1
    talalatok.sort(key=lambda b: (szerep_sorrend.get(b.get("szerep"), 2),
                                  -szam(b.get("prioritas")), zrt(b), not b["ceg"], b["nev"]))
    mezok = ["nev", "nev_tiszta", "ceg", "beosztas", "szerep", "email", "telefon", "prioritas", "kereso_link"]
    w = csv.DictWriter(sys.stdout, fieldnames=mezok, extrasaction="ignore")
    w.writeheader()
    w.writerows(talalatok[: a.max])
    print(f"# telefonkönyv: {len(latott)} egyedi név{' (célcsoport)' if a.celcsoport else ''}, LinkedIn-kapcsolat: {egyezett}, "
          f"nincs LinkedIn-kapcsolat: {len(talalatok)}", file=sys.stderr)


if __name__ == "__main__":
    main()

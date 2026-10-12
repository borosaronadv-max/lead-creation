# LinkedIn-rutin

Napi LinkedIn-jelentés és heti kapcsolatépítési lista Boros Áron profiljához.
A rutin két részből áll:

| Rész | Hol fut | Mit csinál |
|---|---|---|
| **A. Felhős rutin** | ütemezve, Claude Code felhős munkamenet (Gmail + Drive) | napi statisztika és jelentés; hétfőn telefonkönyv-egyeztetés, a heti 20 név beírása a munkalapra |
| **B. Böngészős lépés** | Claude Desktop + Claude in Chrome, Áron gépén, kézzel indítva | profilnézők beolvasása, profilok megkeresése, meghívók előkészítése; a **Küldést Áron hagyja jóvá** |

A két rész a Drive-on lévő [LinkedIn meghívók](https://docs.google.com/spreadsheets/d/1QSTRW8XBr4myeypzQKXsCWUmojhDj94Te5ChPalk6uM/edit)
munkalapon keresztül dolgozik együtt (`Linkedin/` mappa, lapok: `Telefonkönyv`,
`Profilnézők`, `Útmutató`).

## Miért ez a felosztás?

- A felhős rutin megbízhatóan fut akkor is, ha Áron gépe ki van kapcsolva, de a
  LinkedIn felületét nem éri el (nincs belépés, a LinkedIn-nek nincs erre API-ja).
- A böngészős lépés eléri Áron bejelentkezett LinkedIn-jét, de csak akkor fut,
  ha a gép, a Desktop app és a Chrome be van kapcsolva.
- A LinkedIn felhasználási feltételei tiltják az automatizált meghívóküldést, és
  a böngészőből küldött tömeges meghívók is fiókkorlátozást kockáztatnak. Ezért a
  Küldés gombot Áron nyomja meg, vagy legfeljebb 5-ös adagonként kifejezetten
  jóváhagyja. Naponta legfeljebb 20 meghívó megy ki.
- A profilnézők nevét a LinkedIn csak a felületen mutatja (ingyenes fióknál csak
  a legutóbbi néhányat), e-mailben csak a darabszámot küldi.

## Ütemezés

| Rész | Mikor | Tartalom |
|---|---|---|
| A. Napi jelentés | minden nap ~05:45 (Europe/Budapest) | statisztika, 90 napos dinamika, javasolt aktivitás, a munkalap nyitott tételei |
| A. Telefonkönyv-egyeztetés | hétfőnként, a napi futás része | 20 új név a `Telefonkönyv` lapra |
| B. Böngészős lépés | munkanapokon, amikor Áron a gépnél van (kb. 5–10 perc) | profilnézők, profilkeresés, meghívók előkészítése és jóváhagyásos küldése |

Az A rész: „LinkedIn rutin (ebbe a munkamenetbe)”, cron
`CRON_TZ=Europe/Budapest 45 5 * * *`. A 6:00 helyett 5:45: az egész órás
időpontokon torlódik az ütemező, így a jelentés 6-ra biztosan kész. A futás abba a
Claude Code munkamenetbe érkezik, ahol a rutin készült, a jelentés is ott jelenik meg.

## Adatforrások

| Adat | Forrás | Megjegyzés |
|---|---|---|
| Heti bejegyzés-megjelenés | Gmail: `from:notifications-noreply@linkedin.com subject:impressions` — „your posts got N impressions last week”, hétfőnként | a tárgysorból olvasható |
| Profilmegtekintések száma | Gmail: `from:linkedin.com subject:"profile is popular"` — „Your profile is popular - N people” | ritka, rendszertelen; a szám a LinkedIn szerinti utolsó 90 nap |
| Profilmegtekintők nevei | `LinkedIn meghívók` munkalap, `Profilnézők` lap | a B rész írja a linkedin.com/me/profile-views oldalról |
| Meghívók állapota | `LinkedIn meghívók` munkalap, `Telefonkönyv` lap | listázva → előkészítve → elküldve → elfogadva / nincs profil / kihagyva |
| Elfogadott meghívók | Gmail: `from:invitations@linkedin.com subject:accepted` | sikerességmérés |
| Saját kapcsolatok | `Connections.csv` a LinkedIn adatexportból, Google Drive `Linkedin/` mappa (feltöltve 2026-10-12, export: 10-05, 2 386 kapcsolat) | Settings → Data privacy → Get a copy of your data → Connections |
| Telefonkönyv | `telefonk_2607_prior_LP.xlsx`, Google Drive `Linkedin/` mappa, `Kontaktok_Tisztitott` lap (5 568 névjegy, `lp_final_score` prioritással) | 2026-07-17-i export, feltöltve 2026-10-12. Az első futás: 4 682 egyedi névből 1 130 LinkedIn-kapcsolat, 3 552 nem |
| Adatnapló | `data/linkedin-stats.csv` ebben a repóban | minden futás hozzáírja az új értékeket és pusholja |

## 1. Profilmegtekintők

A B rész (böngészős lépés) olvassa be a linkedin.com/me/profile-views oldalt, és a
`Profilnézők` lapra írja az új nézőket (dátum, név, titulus/cég, profil URL, hogy
kapcsolat-e). A nem kapcsolatban lévőkhöz meghívószöveget ír.

A felhős rutin másnap reggel ebből a lapból összesíti a nézőket és a nyitott
meghívókat. Ha a lapra 3 napja nem került új sor, a jelentés egy sorban
emlékeztet a böngészős lépés futtatására.

Kizárás: recruiterek és értékesítők tömeges nézései, névtelen nézők, már függő
meghívó, korábban kihagyott személy.

## 2. Telefonkönyv-egyeztetés (hétfő, A rész)

1. Letölti a telefonkönyv-exportot és a `Connections.csv`-t a Drive-ról.
2. Lefuttatja: `python3 -I scripts/telefonkonyv_egyeztetes.py Connections.csv
   telefonk_2607_prior_LP.xlsx --lap Kontaktok_Tisztitott --prioritas lp_final_score
   --naplo data/linkedin-meghivo-naplo.csv --kapcsolat <export óta elfogadottak> --max 20`. A szkript
   ékezet, titulus („dr.”) és névsorrend nélkül, illetve e-maillel párosít, az
   egyszavas bejegyzéseket („Anyu”) kihagyja. Az export óta elfogadott meghívókat
   (Gmail „accepted your invitation”) is kapcsolatnak kell tekinteni.
3. Akik a telefonkönyvben vannak, de a kapcsolatok között nincsenek: a
   `LinkedIn meghívók` munkalap `Telefonkönyv` lapjára ír 20 új sort (állapot:
   `listázva`), LinkedIn-keresőlinkkel
   (`https://www.linkedin.com/search/results/people/?keywords=<név>+<cég>`) és
   rövid magyar meghívószöveggel (max. 200 karakter, tegeződés/magázódás a
   telefonkönyv-bejegyzés és a Gmail-levelezés alapján).
4. Hetente legfeljebb 20 név (a LinkedIn heti meghívókorlátja ~100, de a
   minőségi, nem tömeges meghívás a cél). Sorrend: `lp_final_score` csökkenő,
   azon belül akinél van cég.
5. Az egyszer már listázott neveket a `data/linkedin-meghivo-naplo.csv` tartja
   nyilván (csak név, cég, dátum — telefonszám és e-mail nem kerül a repóba), ezek
   nem kerülnek újra listára.
6. A `Telefonkönyv` lapon `elfogadva` állapotra állítja azokat, akik a Gmail
   szerint elfogadták a meghívót.

## 3. Böngészős lépés (B rész)

Áron gépén, a Claude Desktop appban, bekapcsolt Claude in Chrome bővítménnyel,
bejelentkezett LinkedIn-nel. Indítás: az alábbi szöveg bemásolása egy új
Desktop-beszélgetésbe.

```
LinkedIn böngészős lépés (lead-creation repó, docs/linkedin-rutin.md).
Nyisd meg a Drive-on a "LinkedIn meghívók" munkalapot.
1) Chrome-ban nyisd meg a linkedin.com/me/profile-views oldalt. Az új nézőket írd
   a Profilnézők lapra (dátum, név, titulus/cég, profil URL, kapcsolat-e). A nem
   kapcsolatban lévőkhöz írj max. 200 karakteres magázó meghívószöveget.
2) A Telefonkönyv lap "listázva" soraira: a keresőlinkkel keresd meg a profilt.
   Ha a cég és a név alapján egyértelmű, írd be a Profil URL-t és állítsd
   "előkészítve"-re. Ha nincs vagy nem egyértelmű, "nincs profil" és megjegyzés.
3) Az "előkészítve" sorokhoz (Profilnézők és Telefonkönyv) nyisd meg a profilt,
   kattints a Kapcsolódás > Megjegyzés hozzáadása gombra, és írd be a
   meghívószöveget. A Küldés gombot NE nyomd meg: mutasd meg 5-ös adagokban a
   neveket, és csak az általam jóváhagyott adagot küldd el. Utána állítsd
   "elküldve"-re. Naponta legfeljebb 20 meghívó.
Ha a LinkedIn ellenőrzést (captcha), figyelmeztetést vagy korlátot jelez, azonnal
állj meg és szólj.
```

A böngészős lépés nem küld üzenetet, nem fogad el és nem utasít el beérkező
meghívót, és nem módosítja a profilt.

## 4. Napi jelentés

```
🔗 LinkedIn – <dátum>

📊 Utolsó 90 nap
Bejegyzés-megjelenés: <összeg> (<hetek száma> hét, átlag <N>/hét)
Profilmegtekintés (LinkedIn 90 napos szám): <N> (előző: <N>, <dátum>)
Havi bontás: <hónap>: <N> (<±%>) · …

📈 Dinamika
- trend, legjobb/leggyengébb hét és valószínű oka (posztolt-e azon a héten),
  volatilitás, hiányzó adat jelzése

🎯 Javasolt aktivitás (max. 3, konkrét, erre a hétre)
- …

👀 Profilnézők (a munkalapról, tegnap óta)
- <név> – <titulus> – kapcsolat? – állapot

📇 Meghívók állapota (munkalap)
listázva: N · előkészítve: N · elküldve: N · elfogadva: N · nincs profil: N
Hétfőn: „20 új név a Telefonkönyv lapon, futtasd a böngészős lépést”

✅ Elfogadott meghívók tegnap óta: <nevek>
```

## Kezdeti adatok (2026-10-12)

Heti bejegyzés-megjelenések (Gmail, hétfői összesítők, a megelőző hétre):

| Hét (e-mail dátuma) | Megjelenés |
|---|---|
| 07-21 | 569 |
| 07-28 | 978 |
| 08-04 | 1 572 |
| 08-11 | 385 |
| 08-18 | 94 |
| 08-25 | 1 608 |
| 09-01 | 927 |
| 09-08 | 595 |
| 09-15 | 2 078 |
| 09-22 | *nincs e-mail* |
| 09-29 | 2 131 |
| 10-06 | 1 278 |

- 90 nap összesen: **12 215** megjelenés 11 jelentett héten (átlag ~1 110/hét).
- Havi átlag/hét: július 774 → augusztus 915 → szeptember 1 433 (**+57%**
  augusztushoz képest) → október eddig 1 278.
- Erős ingadozás (94 – 2 131): a gyenge hetek valószínűleg poszt nélküli hetek;
  a megjelenés szinte teljesen a posztolás gyakoriságán múlik.
- Profilmegtekintés: 94 (10-03) → 96 (10-09), stabil, enyhén nő. Ebből az adatból
  idősor csak a napló gyűlésével lesz.

Javasolt aktivitások a havi értékek növelésére:

1. **Heti 2 poszt fix napokon** (pl. kedd és csütörtök 7:30–8:30): a poszt
   nélküli hetek 100 alá esnek, a rendszeresség simítja a görbét.
2. **A szeptemberi erős posztok formátumát ismételni** (szakmai vélemény,
   magyar nyelvű, tranzakciós/vezetői dilemma témák); a megjelenés első 60
   percében válaszolni minden kommentre.
3. **Napi 10 perc kommentelés** 5–10 célszemély (ügyfélkör, VOSZ/BÉT-kör)
   posztjainál: ez hozza a profilmegtekintéseket, és melegíti a meghívókat.
4. Profil: a fejlécben a Stradamus ajánlat egy mondatban + kiemelt
   (Featured) szekció 1 esettanulmánnyal — a megtekintésből kapcsolat lesz.
5. Hetente 1 rövid hozzászólás/megosztás a meglátogatott eseményekről
   (pl. „Magyar Vállalatok 2030” konferencia), a résztvevők megjelölésével.

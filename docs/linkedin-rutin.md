# LinkedIn-rutin

Napi LinkedIn-jelentés és hetente egyszer kapcsolatépítési lista Boros Áron
profiljához. A rutin a levelezési modellhez hasonlóan **kontrollpontos**: a rutin
elemez, listát és meghívószöveget készít, a LinkedIn-en **meghívót Áron küld**.

## Miért nem küld a rutin magától meghívót?

- A LinkedIn-nek nincs magánszemélyeknek elérhető API-ja a „Ki nézte meg a
  profilomat” listához és a meghívóküldéshez. Az ütemezett rutin felhőben fut,
  LinkedIn-belépés nélkül.
- A LinkedIn felhasználási feltételei tiltják az automatizált (bot/scraper)
  kapcsolódást; az ilyen fiókokat a LinkedIn korlátozza vagy letiltja. Egy
  CEO-profilnál ez nem éri meg a kockázatot.
- A profilmegtekintők nevét a LinkedIn csak a felületen mutatja (ingyenes
  fióknál csak az utolsó néhányat), e-mailben csak a darabszámot küldi.

Ezért a rutin: kigyűjti, ami az adatforrásokból elérhető, és **kattintásra kész
listát** ad (profil-/keresőlink + személyre szabott meghívószöveg). A küldés
naponta 2–5 perc Áron részéről.

## Ütemezés

| Rész | Mikor | Tartalom |
|---|---|---|
| Napi jelentés | minden nap ~05:45 (Europe/Budapest) | statisztika, 90 napos dinamika, javasolt aktivitás, profilmegtekintők teendőlistája |
| Telefonkönyv-egyeztetés | hétfőnként, a napi futás része | telefonkönyv ↔ LinkedIn-kapcsolatok összevetése, meghívólista |

Megvalósítás: „LinkedIn rutin (ebbe a munkamenetbe)”, cron
`CRON_TZ=Europe/Budapest 45 5 * * *`. A 6:00 helyett 5:45: az egész órás
időpontokon torlódik az ütemező, így a jelentés 6-ra biztosan kész. A futás abba a
Claude Code munkamenetbe érkezik, ahol a rutin készült (itt van Gmail- és
Drive-hozzáférés), a jelentés is ott jelenik meg.

## Adatforrások

| Adat | Forrás | Megjegyzés |
|---|---|---|
| Heti bejegyzés-megjelenés | Gmail: `from:notifications-noreply@linkedin.com subject:impressions` — „your posts got N impressions last week”, hétfőnként | a tárgysorból olvasható |
| Profilmegtekintések száma | Gmail: `from:linkedin.com subject:"profile is popular"` — „Your profile is popular - N people” | ritka, rendszertelen; a szám a LinkedIn szerinti utolsó 90 nap |
| Profilmegtekintők nevei | csak a LinkedIn felületén | e-mailben nem jön; lásd 1. lépés |
| Elfogadott meghívók | Gmail: `from:invitations@linkedin.com subject:accepted` | sikerességmérés |
| Saját kapcsolatok | `Connections.csv` a LinkedIn adatexportból, Google Drive `LinkedIn/` mappa | Settings → Data privacy → Get a copy of your data → Connections |
| Telefonkönyv | `contacts.csv` / `.vcf` Google Drive `LinkedIn/` mappa | Google Contacts → Export, vagy iPhone-ról vCard |
| Adatnapló | `data/linkedin-stats.csv` ebben a repóban | minden futás hozzáírja az új értékeket és pusholja |

## 1. Profilmegtekintők (napi)

A rutin a Gmailből nem tudja a neveket, ezért:

1. Ha Áron a `LinkedIn/profilnezok.txt` Drive-fájlba bemásolja a
   linkedin.com/me/profile-views oldal listáját (név, titulus — elég kijelölni és
   bemásolni), a rutin összeveti a `Connections.csv`-vel, és a **nem kapcsolatban
   lévőkre** meghívószöveget ír.
2. Ha nincs új bemásolt lista, a jelentés egy sorban emlékeztet a link
   megnyitására.

Kizárás: recruiterek/értékesítők tömeges nézései, névtelen nézők, már függő
meghívó (a `Connections.csv` és a korábbi listák alapján), korábban elutasított
személy.

## 2. Telefonkönyv-egyeztetés (hétfő)

1. Beolvassa a telefonkönyv-exportot és a `Connections.csv`-t a Drive-ról.
2. Normalizált névvel (ékezet, „dr.”, sorrend: Vezetéknév Keresztnév ↔ First
   Last) és e-mail/cégnévvel párosít.
3. Akik a telefonkönyvben vannak, de a kapcsolatok között nincsenek: lista
   LinkedIn-keresőlinkkel
   (`https://www.linkedin.com/search/results/people/?keywords=<név>+<cég>`) és
   rövid magyar meghívószöveggel (max. 200 karakter, tegeződés/magázódás a
   telefonkönyv-bejegyzés és a Gmail-levelezés alapján).
4. Hetente legfeljebb 20 név (a LinkedIn heti meghívókorlátja ~100, de a
   minőségi, nem tömeges meghívás a cél). Prioritás: akivel az elmúlt 12 hónapban
   volt levelezés.
5. Az egyszer már listázott neveket a `data/linkedin-meghivo-naplo.csv` tartja
   nyilván, nem kerülnek újra listára 90 napig.

## 3. Napi jelentés

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

👀 Profilmegtekintők → meghívó (ha van bemásolt lista)
- <név> – <titulus> – <link> – „<meghívószöveg>”

📇 Telefonkönyv → meghívó (csak hétfőn)
- <név> – <cég> – <keresőlink> – „<meghívószöveg>”

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

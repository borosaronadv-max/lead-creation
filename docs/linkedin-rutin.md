# LinkedIn-rutin

Heti (hétfői) LinkedIn-jelentés és kapcsolatépítési lista
Boros Áron profiljához. A rutin részei:

| Rész | Hol fut | Mit csinál |
|---|---|---|
| **A. Felhős rutin** | ütemezve, Claude Code felhős munkamenet (Gmail + Drive) | hétfőnként: statisztika és jelentés, telefonkönyv-egyeztetés, a heti 40 célcsoport-jelölt beírása a munkalapra |
| **H. Havi rutin** | böngésző (adatgyűjtés, meghívók); a felhős havi kimutatás 2026-10-22-től megszűnt | posztreakciók kimutatása, reagálók és 2. fokú CEO/CFO/tulajdonosok meghívása |
| **B. Böngészős lépés** | Claude Desktop + Claude in Chrome, Áron gépén, kézzel indítva | profilnézők beolvasása, profilok megkeresése, meghívók előkészítése; a **Küldést Áron hagyja jóvá** |

A részek a Drive-on lévő [LinkedIn meghívók](https://docs.google.com/spreadsheets/d/1QSTRW8XBr4myeypzQKXsCWUmojhDj94Te5ChPalk6uM/edit)
munkalapon keresztül dolgozik együtt (`Linkedin/` mappa, lapok: `Telefonkönyv`,
`Profilnézők`, `Posztok`, `Reakciók`, `2. fokú`, `Útmutató`).

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
| A. Heti jelentés | hétfőnként ~05:45 (Europe/Budapest) | statisztika, 90 napos dinamika, javasolt aktivitás, a munkalap nyitott tételei |
| A. Telefonkönyv-egyeztetés | hétfőnként, a heti futás része | 40 célcsoport-jelölt a `Telefonkönyv` lapra (tulajdonos/CEO/CFO, árbevétel-ellenőrzésre) |
| H. Havi böngészős lépés | minden hónap 1–4. napja, egyszer (kb. 20–30 perc) | előző havi posztok és reagálók, 2. fokú célcsoport-jelöltek a munkalapra |
| B. Böngészős lépés | munkanapokon, amikor Áron a gépnél van (kb. 5–10 perc) | profilnézők, profilkeresés, meghívók előkészítése és jóváhagyásos küldése |

Az A rész: „LinkedIn heti rutin – hétfő (ebbe a munkamenetbe)”, cron
`CRON_TZ=Europe/Budapest 45 5 * * 1` (2026-10-22-ig naponta futott). A 6:00 helyett 5:45: az egész órás
időpontokon torlódik az ütemező, így a jelentés 6-ra biztosan kész. A futás abba a
Claude Code munkamenetbe érkezik, ahol a rutin készült, a jelentés is ott jelenik meg.

### Futtatási környezet

A felhős rutin (A) futásához ez kell:

| Mi | Érték | Hol állítható |
|---|---|---|
| Repó | `borosaronadv-max/lead-creation` | claude.ai/code → Routines → a rutin → Repositories |
| Ág | `claude/trusting-thompson-q7unak`, írási joggal (a `data/*.csv` commit + push miatt) | ugyanott |
| Csatlakozók | Gmail, Google Drive, Google Sheets | claude.ai/code → Routines → a rutin → Connectors |

| Rutin | Trigger ID | Ütemezés |
|---|---|---|
| LinkedIn heti rutin (hétfő) | `trig_01PcJe1Xg7135ERnG4hSTDi4` | `CRON_TZ=Europe/Budapest 45 5 * * 1` |

A havi felhős rutint (`trig_01W6e1fwyP8VDVjyTnRvePkn`) 2026-10-22-én töröltük.

Az ütemezett futás abba a munkamenetbe érkezik, ahol a rutin készült; ott a repó
és a csatlakozók rendelkezésre állnak. A felületről kézzel indított futás („Run
now”) új munkamenetet nyithat, amelyben csak az lesz elérhető, amit a rutin
beállításában megadtak. A csatlakozókat a rutinhoz eszközzel nem lehet
hozzárendelni, ezt a felületen kell bekapcsolni.

**E-mailes riport:** a felhős rutin a futás végén elküldi a kész riportot a
`mcp__Microsoft_365__outlook_send_mail` eszközzel, kizárólag a boros.aron@stradamus.hu
címre (cc/bcc nélkül), tárgy: „LinkedIn heti rutin – ÉÉÉÉ.HH.NN.”, HTML törzzsel. Ez az egyetlen engedélyezett küldés. Ha nem sikerül,
a riport elejére „⚠️ E-mail küldés sikertelen: <ok>” kerül.

Ha mégis üres munkakönyvtárban, csatlakozók nélkül indul a futás, az utasítás 0.
lépése szerint:
- a repót az `add_repo` eszközzel (owner `borosaronadv-max`, repo `lead-creation`,
  access `push`) adja hozzá, klónozza és checkoutolja az ágat;
- ha a Gmail, Drive vagy Sheets nem érhető el, a jelentés elején egy sorban jelzi,
  melyik hiányzik, a többi lépést lefuttatja, repó nélkül pedig nem ír CSV-t.

### Naptár (Gmail + céges Outlook)

A böngészős lépések és a posztolás időkerete ismétlődő eseményként a
boros.aron.adv@gmail.com naptárban, a boros.aron@stradamus.hu naptárba meghívóként:

| Esemény | Mikor | Időkeret |
|---|---|---|
| LinkedIn – napi meghívók + kommentelés | K–P 17:30 | 20 perc |
| LinkedIn – heti célcsoport-lista: árbevétel + meghívók | H 17:30 | 40 perc |
| LinkedIn – poszt megírása és közzététele | H, Sze 08:00 | 30 perc |
| LinkedIn – havi poszt- és reakció-áttekintés, 2. fokú lista | a hónap első munkanapja 18:15 | 30 perc |

Összesen kb. 3 óra hetente, plusz 30 perc havonta. A 2026-10-22 – 11-01 közötti
szabadság alatti alkalmak törölve.

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

**Célcsoport:** 2–20 Mrd Ft árbevételű cégek tulajdonosai, CEO-i (vezérigazgató,
ügyvezető, managing director) és CFO-i (pénzügyi/gazdasági igazgató).

1. Letölti a telefonkönyv-exportot és a `Connections.csv`-t a Drive-ról.
2. Lefuttatja:
   `python3 -I scripts/telefonkonyv_egyeztetes.py Connections.csv telefonk_2607_prior_LP.xlsx
   --lap Kontaktok_Tisztitott --celcsoport --prioritas priority_score_10
   --naplo data/linkedin-meghivo-naplo.csv --kapcsolat <export óta elfogadottak> --max 40`
   - Párosítás ékezet, titulus és névsorrend nélkül, illetve e-maillel; egyszavas
     bejegyzések kimaradnak. Az export óta elfogadott meghívók kapcsolatnak számítanak.
   - `--celcsoport`: csak a tulajdonos/CEO/CFO beosztásúak; helyettesek,
     asszisztensek kimaradnak. Kizárt szervezetek: bankok, állami és önkormányzati
     hivatalok, oktatás, egyesületek, klaszterek, alapkezelők és befektetők, Big4,
     multinacionális és ismerten 20 Mrd Ft fölötti cégcsoportok.
   - Sorrend: `priority_score_10` csökkenő, azon belül a Zrt.-k előre.
   - Első futás (2026-10-13): 4 682 egyedi névből 366 célcsoport-szerep, ebből
     152 már kapcsolat, 214 nem.
3. **Az árbevételt a névjegyek nem tartalmazzák, és a felhős környezet nem éri el
   a cégadatbázisokat** (Opten, céginformáció, e-beszámoló). Ezért a rutin hetente
   40 jelöltet ír a `Telefonkönyv` lapra (állapot: `listázva`, az
   `Árbevétel (Mrd Ft)` oszlop üres), és az árbevételt a böngészős lépés ellenőrzi.
   Ha Áron feltölt egy árbevétel-exportot (pl. Opten-lista adószámmal/cégnévvel) a
   `Linkedin/` mappába, a rutin azzal előre szűr.
4. Meghívószöveg (max. 200 karakter, magázó): tulajdonos/CEO: „…cégvezetőként
   szívesen tartanám Önnel LinkedInen is a kapcsolatot…”; CFO: „…finanszírozási
   témákban szívesen tartanám…”.
5. A listázott neveket a `data/linkedin-meghivo-naplo.csv` tartja nyilván (csak név,
   cég, dátum; telefonszám és e-mail nem kerül a repóba), ezek nem kerülnek újra
   listára.
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
2) A Telefonkönyv lap "listázva" soraira, felülről:
   a) Árbevétel: nézd meg a cég legutóbbi nettó árbevételét (ceginformacio.hu,
      opten.hu vagy e-beszamolo.im.gov.hu), írd az "Árbevétel (Mrd Ft)" oszlopba.
      Ha 2 Mrd Ft alatti vagy 20 Mrd Ft fölötti, állapot: "kihagyva – árbevétel".
      Ha a cég nem azonosítható, megjegyzés és "kihagyva".
   b) A sávba esőknél a keresőlinkkel keresd meg a profilt. Ha a cég és a név
      alapján egyértelmű, írd be a Profil URL-t és állítsd "előkészítve"-re.
      Ha nincs vagy nem egyértelmű: "nincs profil" és megjegyzés.
3) Az "előkészítve" sorokhoz (Profilnézők, Telefonkönyv, Reakciók, 2. fokú) nyisd meg a profilt,
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
Hétfőn: „40 új célcsoport-jelölt a Telefonkönyv lapon, futtasd a böngészős lépést”

✅ Elfogadott meghívók tegnap óta: <nevek>
```

## 5. Havi rutin (posztreakciók és 2. fokú célcsoport)

### H1. Havi böngészős lépés (Áron gépén, a hónap 1–4. napján)

Indítás: az alábbi szöveg egy új Claude Desktop-beszélgetésben, bekapcsolt Claude in
Chrome bővítménnyel és bejelentkezett LinkedInnel.

```
LinkedIn havi böngészős lépés (lead-creation repó, docs/linkedin-rutin.md, 5. pont).
Munkalap: Drive "LinkedIn meghívók". Hónap = az előző naptári hónap (ÉÉÉÉ-HH).
1) Posztok: a linkedin.com/in/me/recent-activity/all/ oldalon az előző hónap saját
   posztjait írd a Posztok lapra (dátum, URL, első sor, formátum, megjelenés,
   reakció, komment, megosztás; a számok a poszt alatti elemzésből).
2) Reakciók: minden posztnál nyisd meg a reakciók listáját, és minden reagálót írd
   a Reakciók lapra (név, titulus, cég, fokozat 1./2./3., reakció típusa, profil URL).
   Szerep: "tulajdonos"/"CEO"/"CFO"/"egyéb" a titulus alapján. 1. fokúaknál
   Állapot = "kapcsolat". A többieknél (2./3. fok) Állapot = "listázva" és max. 200
   karakteres magázó meghívószöveg: "Tisztelt <Név>! Köszönöm, hogy reagált a
   bejegyzésemre; örülnék, ha LinkedInen is kapcsolatban maradnánk. Üdvözlettel:
   Boros Áron". Ha a reagáló több posztra is reagált, egy sor elég (megjegyzés: hány).
3) 2. fokú célcsoport: LinkedIn-keresés, Emberek, Kapcsolatok: 2. fok, Hely:
   Magyarország, kulcsszó egyenként: CEO, CFO, vezérigazgató, ügyvezető, pénzügyi
   igazgató, alapító, founder, tulajdonos, owner. A találatokból max. 40 főt írj a
   "2. fokú" lapra (név, titulus, cég, szerep, profil URL, közös kapcsolatok száma),
   előre a több közös kapcsolattal rendelkezőket. Ne vedd fel, aki a Telefonkönyv
   vagy a 2. fokú lapon már szerepel. Ellenőrizd a cég árbevételét (ceginformacio.hu,
   opten.hu vagy e-beszamolo.im.gov.hu): 2 Mrd Ft alatt vagy 20 Mrd Ft fölött
   "kihagyva – árbevétel". A sávba esőknél meghívószöveg: "Tisztelt <Név>! Közös
   ismerőseink révén figyeltem fel Önre; cégvezetőként szívesen kapcsolódnék
   LinkedInen is. Üdvözlettel: Boros Áron, Stradamus" (CFO-nál: "...pénzügyi
   vezetőként..."), állapot "előkészítve".
4) Meghívók: a Reakciók és a 2. fokú lap "listázva"/"előkészítve" soraihoz nyisd
   meg a profilt, Kapcsolódás > Megjegyzés hozzáadása, írd be a szöveget. A Küldés
   gombot NE nyomd meg: 5-ös adagokban mutasd a neveket, és csak a jóváhagyott
   adagot küldd el, utána "elküldve". Az összes lapról együtt legfeljebb 20
   meghívó naponta; ami ma nem fér bele, azt a napi böngészős lépés küldi tovább.
Ha a LinkedIn ellenőrzést (captcha), figyelmeztetést, keresési vagy meghívókorlátot
jelez, azonnal állj meg és szólj.
```

Megjegyzések:
- Saját profil posztjainál a LinkedIn nem ad „meghívás követésre” funkciót (az a
  céges oldalaké), ezért a nem kapcsolatban lévő reagálók kapcsolódási meghívót kapnak.
- A LinkedIn ingyenes fióknál havonta korlátozza a keresések számát (commercial use
  limit), ezért a 2. fokú keresés havi egyszeri, legfeljebb 40 fős.
- Az 1. fokú (már meglévő) kapcsolatok közül 616 fő tulajdonos/CEO/CFO szerepkörű
  (2026-10-13); nekik nem megy meghívó.

### H2. Havi kimutatás (felhő) – megszűnt

A havi ütemezett futást 2026-10-22-én töröltük; a formátum kérésre, kézzel futtatva
használható. A Posztok és Reakciók lap előző havi soraiból, valamint a Gmail heti
megjelenés-összesítőiből:

```
📣 LinkedIn havi kimutatás – <ÉÉÉÉ-HH>

📝 Posztok: N db · megjelenés össz.: N · reakció: N · komment: N · megosztás: N
Reakció / 1000 megjelenés: N (előző hónap: N)
Top 3 poszt: <dátum> – <első sor> – <reakció>/<megjelenés>
Leggyengébb: <dátum> – <első sor> – miért (formátum, időpont, téma)

👥 Reagálók: N egyedi fő (1. fok: N · 2. fok: N · 3. fok: N)
Szerep: tulajdonos N · CEO N · CFO N · egyéb N
Visszatérő reagálók (2+ poszt): <nevek>
Meghívók a reagálóknak: listázva N · elküldve N · elfogadva N

🎯 2. fokú célcsoport: listázva N · kihagyva – árbevétel N · elküldve N · elfogadva N

💡 Következő hónapra (max. 3): téma, formátum, időpont a top posztok alapján
```

Ha a Posztok lapon nincs előző havi sor, a kimutatás helyett egy sor: a havi
böngészős lépés még nem futott. A heti jelentés a hónap első hétfőjén emlékeztet rá.

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

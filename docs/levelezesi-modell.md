# Levelezési modell kontrollpontokkal

A Gmail-postafiók (boros.aron.adv@gmail.com) feldolgozását egy ütemezett Claude-rutin
végzi. A rutin **soha nem küld levelet**: csak címkéz, piszkozatot ír és összefoglal.
Minden kimenő levelet Áron küld el, ez az első kontrollpont.

## Ütemezés és fiókok

Munkanapokon (H–P) egyszer, ~5:00-kor (Europe/Budapest; cron
`CRON_TZ=Europe/Budapest 57 4 * * 1-5`). Magyar munkaszüneti napon (pl. 2026-10-23,
2026-12-24, 2026-12-25) a rutin elindul, de nem dolgoz fel semmit; a következő munkanap
az egész kimaradt időszakot pótolja. Rutin: „Levelezési triázs – Gmail + Outlook
(munkanapokon, ebbe a munkamenetbe)”. A futás abba a Claude Code munkamenetbe érkezik, ahol a modell
készült; az összefoglaló ott jelenik meg.

Két fiók:

| Fiók | Cím | Jelölés módja |
|---|---|---|
| [G] Gmail | boros.aron.adv@gmail.com | `Triázs/*` címkék (lent) |
| [O] Outlook / Microsoft 365 | boros.aron@stradamus.hu | `Triázs-*` kategóriák, ugyanazokkal a nevekkel (`Triázs-Ügyfél-mandátum`, `Triázs-Partner`, `Triázs-Admin`, `Triázs-Hírlevél`, `Triázs-Sürgős`, `Triázs-Döntésre-vár`, `Triázs-Piszkozat-kész`, `Triázs-Követés`) |

„Új” levél = az előző munkanapi futás óta érkezett/küldött (+2 óra ráhagyás); hétfőn ez
a pénteki futás óta. Az Outlookban a kategóriára
`category:"Triázs-Követés"` lekérdezéssel lehet keresni. Mindkét fiókban csak piszkozat
készülhet (Gmail `create_draft`, Outlook `outlook_create_reply_draft` /
`outlook_create_reply_all_draft`); küldés, továbbítás, törlés, mozgatás tilos.


## Outlook-mappák (témaarchívum)

Áron a fontos céges leveleket kézzel, témánként mappákba teszi a Beérkezett üzenetek alatt;
a többit törli. A rutin a mappákba **nem mozgat**, de használja őket:

- **Kategorizáláshoz** – a mappaszerkezet a témák térképe:
  - `ügyfelek/`: Carion · DSTP · lead · oportunity · PC-Trade · Qtics_Tamcert · SZIGÜ
  - `Stradamus/`: advisory_board · compliance · CRM · ESG_üzletág · iránytű_projekt · könyvvizsgálat · portál · PR
  - `Magán/`: HVCA · IVSZ · JVSZ_gnioMB · leadek_infok · Nexum · NOAA · PMSZ · Tata MGZRT
- **Követéshez** – a válaszokat minden mappában keresi, mert egy válasz már iktatva is lehet.
- **Iktatási javaslathoz** – a napi összefoglalóban „📁 Iktatási javaslat” szekció mondja
  meg, melyik új levél melyik mappába illik, és hány hírlevél/értesítő törölhető.

## 1. Triázs (címkézés)

Feldolgozandó: a beérkezett mappa szálai az utolsó 3 napból, amelyeken még nincs
`Triázs/*` kategóriacímke (a saját küldött levelek, spam és kuka kizárva):

```
in:inbox newer_than:3d -in:sent -label:triázs-ügyfél-mandátum -label:triázs-partner -label:triázs-admin -label:triázs-hírlevél
```

> Gmail-keresésben a címkét **névvel** kell megadni (`label:triázs-hírlevél`); az ID-vel
> (`label:Label_127`) a keresés nem szűr. Címkézéshez (`label_thread`) viszont az ID kell.
> Ezt az első tesztfutás (2026-10-12) derítette ki.

Kategóriacímkék (szálanként pontosan egy):

| Címke | Gmail ID | Mi kerül ide |
|---|---|---|
| `Triázs/Ügyfél-mandátum` | `Label_124` | Ügyfél, megbízás, ajánlat, futó mandátum, tranzakció, delivery |
| `Triázs/Partner` | `Label_125` | Alvállalkozók, szakmai partnerek, egyesületek (VOSZ, BÉT, ÓE stb.), együttműködők |
| `Triázs/Admin` | `Label_126` | Számlák, könyvelés, hivatalos/hatósági levelek, HR, bank, belső értekezlet-meghívók, iskola/család ügyintézés, rendszerértesítések |
| `Triázs/Hírlevél` | `Label_127` | Hírlevelek, marketing, eseménymeghívók tömeges listáról, automatikus értesítők |

Állapotcímkék (opcionálisak, több is lehet):

| Címke | Gmail ID | Mikor |
|---|---|---|
| `Triázs/Sürgős` | `Label_128` | Határidő 48 órán belül, ügyfél sürget, hatósági/fizetési határidő, eszkaláció |
| `Triázs/Piszkozat-kész` | `Label_129` | A rutin válaszpiszkozatot készített a szálhoz |
| `Triázs/Követés` | `Label_131` | Áron kimenő levelében kérés vagy vállalás van, amit követni kell |
| `Triázs/Döntésre-vár` | `Label_130` | Áron döntése/tartalmi inputja kell (ár, vállalás, igen/nem, stratégiai kérdés) |

A meglévő `INBOX/Stradamus/...` és `INBOX/Magán/...` címkékhez a rutin nem nyúl, és
nem archivál, nem töröl, nem jelöl olvasottnak semmit.

## 2. Válaszpiszkozatok — 1. kontrollpont

- Csak **rutinlevélre** készül piszkozat: visszaigazolás, időpont-egyeztetés,
  dokumentum átvételének nyugtázása, egyszerű információkérés, amire a szálból
  egyértelmű a válasz.
- **Nem** készül piszkozat: hírlevélre, automatikus értesítőre, és olyan levélre,
  ahol ár, vállalás, jogi/szerződéses kérdés vagy stratégiai döntés kell — ezek
  `Triázs/Döntésre-vár` címkét kapnak.
- A piszkozat válaszként, a szálban jön létre, a levél nyelvén (alapból magyar),
  tegeződés/magázódás a korábbi levelezést követi, aláírás: „Üdvözlettel, Boros Áron”.
- Bizonytalan adatot nem talál ki, hanem `[[...]]` jelöléssel hagy helyet.
- **Elküldeni csak Áron küldi.** A rutin semmilyen küldő/továbbító eszközt nem használ.


## 2/b. Követés – kimenő levelek (amit Áron kért vagy vállalt)

Minden futás átnézi a kimenő leveleket (`in:sent newer_than:3d -label:triázs-követés`).
Ha Áron **kért** valamit valakitől (küldjön, nézze meg, hívja fel, jelezzen vissza,
véleményezze), vagy **vállalt** valamit („küldöm”, „beteszem a naptárba”, „jelentkezem”),
a szál `Triázs/Követés` (`Label_131`) címkét kap.

A nyitott követéseket (`label:triázs-követés`) a rutin minden futáskor újraolvassa:

- **Típus:** „Várok rá” (más felé kért) vagy „Saját teendő” (Áron vállalta).
- **Állapot:** nincs válasz / visszaigazolta, folyamatban / részben teljesült / teljesült.
  Teljesült tételről a címke lekerül, és „✅ Lezárult” sorban jelenik meg.
- **Prioritás:**
  - **P1** – lejárt vagy 2 napon belül lejáró határidő, ügyfél/pénz/hatóság, vagy a másik
    fél által ígért időpont már elmúlt;
  - **P2** – 5+ munkanapja nincs válasz, vagy a saját vállalás még nem látszik teljesítettnek;
  - **P3** – minden más.
- **Emlékeztető-piszkozat:** P1/P2 „Várok rá” tételnél, ha 5+ munkanapja nincs válasz
  (vagy az ígért időpont 2+ munkanapja elmúlt), a rutin udvarias emlékeztető-piszkozatot
  írhat. Elküldeni ezt is csak Áron küldi.

A napi összefoglalóban a teljes követési lista megjelenik, fiók-jelöléssel ([G]/[O]).

## 3. Napi összefoglaló — 2. kontrollpont

A rutin futásának végén rövid lista (a rutin értesítőjében jelenik meg):

```
📬 Levelezés – <dátum> <reggeli|délutáni>
Feldolgozva: N szál (Ügyfél x · Partner y · Admin z · Hírlevél w)

🔴 Sürgős
- <feladó> – <tárgy> – miért sürgős, határidő

✍️ Piszkozat kész (átnézésre, küldés nálad)
- <feladó> – <tárgy> – 1 mondat a válaszról

📌 Követés (amit te kértél / vállaltál) – prioritás szerint
P1 / P2 / P3
- [Várok rá|Saját] <kitől/kinek> – <mit> – kérve: <dátum> – állapot – javasolt lépés
✅ Lezárult: <tétel>

⚖️ Döntésre vár
- <feladó> – <tárgy> – mi a kérdés, javasolt opciók

ℹ️ Tudnivaló (opcionális, max 3 sor; nem kell rá válasz)
```

Üres szekció helyett „—”. Minden tétel előtt [G] (Gmail) vagy [O] (Outlook) jelzi a fiókot.

Jelszó, belépési adat és bankszámlaszám nem kerül az összefoglalóba.

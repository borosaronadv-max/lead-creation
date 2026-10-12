# Levelezési modell kontrollpontokkal

A Gmail-postafiók (boros.aron.adv@gmail.com) feldolgozását egy ütemezett Claude-rutin
végzi. A rutin **soha nem küld levelet**: csak címkéz, piszkozatot ír és összefoglal.
Minden kimenő levelet Áron küld el, ez az első kontrollpont.

## Ütemezés

Hétköznap (H–P), Europe/Budapest időzóna, két futás:

| Futás | Időpont | Tartalom |
|---|---|---|
| Reggeli | ~7:30 | triázs + piszkozatok + **napi összefoglaló** |
| Délutáni | ~13:30 | triázs + piszkozatok + rövid frissítés (csak az új tételek) |

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

## 3. Napi összefoglaló — 2. kontrollpont

A rutin futásának végén rövid lista (a rutin értesítőjében jelenik meg):

```
📬 Levelezés – <dátum> <reggeli|délutáni>
Feldolgozva: N szál (Ügyfél x · Partner y · Admin z · Hírlevél w)

🔴 Sürgős
- <feladó> – <tárgy> – miért sürgős, határidő

✍️ Piszkozat kész (átnézésre, küldés nálad)
- <feladó> – <tárgy> – 1 mondat a válaszról

⚖️ Döntésre vár
- <feladó> – <tárgy> – mi a kérdés, javasolt opciók

ℹ️ Tudnivaló (opcionális, max 3 sor; nem kell rá válasz)
```

Üres szekció helyett „—”. A délutáni futás csak az új tételeket sorolja fel, plusz a
reggel óta még nyitott sürgős tételeket.

Jelszó, belépési adat és bankszámlaszám nem kerül az összefoglalóba.

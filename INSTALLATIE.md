# Klanten-aankondiger installeren

Na de installatie werkt het zo: je maakt een nieuwe post in **📋-klanten**, en binnen een half uur zet de bot in **#aankondigingen** een bericht met de naam van de klant, de tags, de info uit je post en een link ernaartoe. Daarbij tagt hij `@Editor`, dus iedereen krijgt een melding.

De bot draait gratis op GitHub. Je hebt geen eigen server nodig en je pc hoeft niet aan te staan. Reken op ongeveer 15 minuten om alles in te stellen. Dat hoeft maar één keer.

---

## Stap 1: maak de bot aan in Discord

1. Ga naar https://discord.com/developers/applications en log in.
2. Klik op **New Application**, noem hem `Ace Klanten Bot` en klik op **Create**.
3. Ga links naar **Bot**, klik op **Reset Token** en kopieer de token.
   ⚠️ Die token is het wachtwoord van je bot. Deel hem met niemand en plak hem nergens anders dan in stap 4.
4. Ga links naar **OAuth2** en dan naar **URL Generator**.
   - Vink bij *Scopes* het vakje `bot` aan.
   - Vink bij *Bot Permissions* aan: `View Channels`, `Send Messages`, `Embed Links`, `Read Message History` en `Mention Everyone`. Die laatste is nodig om `@Editor` te mogen taggen.
5. Kopieer de link die onderaan verschijnt, open hem en kies de server **Ace Creative Agency**.

## Stap 2: laat de bot posten in #aankondigingen

In #aankondigingen mag alleen jij posten, dus de bot moet daar apart toestemming krijgen.

1. Ga naar **#aankondigingen**, kies **Kanaal bewerken** en dan **Machtigingen**.
2. Voeg onder *Geavanceerde machtigingen* de rol **Ace Klanten Bot** toe.
3. Zet `Berichten verzenden` en `Links insluiten` op ✅ en sla op.

## Stap 3: zoek het ID van de Editor-rol op

De andere ID's staan hieronder al ingevuld. Alleen die van de rol Editor moet je zelf opzoeken.

1. Ga in Discord naar **Gebruikersinstellingen**, dan **Geavanceerd**, en zet **Ontwikkelaarsmodus** aan.
2. Ga naar **Serverinstellingen**, dan **Rollen**, klik op de drie puntjes naast **Editor** en kies **Rol-ID kopiëren**.

## Stap 4: zet de bot op GitHub

1. Maak een (gratis) account op https://github.com als je die nog niet hebt.
2. Klik op **New repository**, noem hem `ace-klanten-bot`, kies **Private** en klik op **Create repository**.
3. Klik op **uploading an existing file** en sleep de **inhoud** van de map `klanten-bot` erin, dus het bestand `announce.py` en de map `.github`. Klik op **Commit changes**.
   Tip: zie je de map `.github` niet op je computer? Op een Mac druk je in Finder op `Cmd + Shift + .` en op Windows zet je in Verkenner *Verborgen items* aan.
4. Ga naar **Settings**, dan **Secrets and variables** en **Actions**, en klik vijf keer op **New repository secret**:

| Naam | Waarde |
|---|---|
| `DISCORD_TOKEN` | de token uit stap 1 |
| `GUILD_ID` | `1559600785124364400` |
| `FORUM_CHANNEL_ID` | `1560280156533424208` |
| `ANNOUNCE_CHANNEL_ID` | `1559601590598373386` |
| `EDITOR_ROLE_ID` | het ID uit stap 3 |

## Stap 5: testen

1. Ga in je repository naar het tabblad **Actions**. Klik op **Klanten aankondigen** en dan op **Run workflow**.
2. Na een halve minuut zie je een groen vinkje. In het logboek staat *"Geen nieuwe klantposts gevonden."* Dat klopt, want de negen bestaande klanten zijn ouder dan 24 uur en worden dus niet opnieuw aangekondigd.
3. Maak de volgende keer gewoon een nieuwe klantpost aan. Binnen 30 minuten staat hij in #aankondigingen.

---

## Goed om te weten

- **Waarom 30 minuten?** Een private repository heeft 2.000 gratis minuten per maand. Elke 30 minuten checken gebruikt er ongeveer 1.450, dus het blijft gratis. GitHub start soms een paar minuten later dan gepland, en dat is normaal.
- **Dubbele berichten?** Die komen er niet. De bot kijkt eerst in #aankondigingen welke klanten hij al heeft aangekondigd.
- **Wil je hem direct laten posten?** Klik dan in Actions op **Run workflow**.
- **Werkt er iets niet?** Een rood kruisje in Actions betekent bijna altijd dat de bot een recht mist (stap 2) of dat een van de waarden in stap 4 niet klopt. In het logboek staat welke.
- **Stoppen?** Ga in Actions naar **Klanten aankondigen**, klik op de drie puntjes en kies **Disable workflow**.

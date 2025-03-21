# Personlig Regnskap Bot (for Handelsbanken)
Et enkelt program som skaffer en .csv fil med banktransaksjonene dine fra Handelsbanken, leser den, og fører månedlig regnskap automatisk i Google Sheets

# Introduksjon
Som student liker jeg å ha oversikt over hvor mye penger jeg bruker. I starten av studietiden førte jeg manuelt hver utgift inn i et google forms, som la dette inn i et regnskap i google sheets. Men en dag fant jeg ut at banken lar deg laste ned transaksjoner som en .csv fil, og at det finnes et python bibliotek som kan skrive til google sheets. Da skjønte jeg at hele prosessen min med å føre regnskap kunne automatiseres. Resultatet var at jeg skrev dette enkle python programmet.

# Disclaimer
Jeg har Handelsbanken, så så langt jeg vet fungerer dette programmet kun for handelsbanken. Men det går sikkert an å tilpasse til andre banker uten alt for mye jobb.
Jeg har også kun lagt inn to kategorier, dagligvarer og transport, siden dette er de to eneste kategoriene jeg egentlig bryr meg om å se, i tillegg til totale utgifter selvsagt.
Som student bryr jeg meg om å se hvordan utgiftene mine ligger an ift. lånekassens lån og stipend. Derfor ligger dette inne i regnearket.

Det krever litt oppsett og tilpasning for å få programmet til å fungere. Men det er et morsomt lite prosjekt, som kan hjelpe deg å få kontroll på utgiftene dine! 
Når programmet fungerer kreves det bare 1 minutt i måneden for å føre regnskapet ditt!

# Virkemåte
Programmet har et enkelt CLI. Den vil be deg hvilken måned du vil føre regnskap for (den tar bare en måned om gangen). Deretter vil den åpne et vindu med handelsbankens innloggingsside. Den vil så vente til du har logget inn, før den trykker seg inn på kontoen din, fyller inn de valgte datoene og laster ned en .csv fil med transaksjonene for den valgte måneden. Den vil så lese .csv filen, summere utgifter og inntekter hver for seg, summere utgifter til transport og dagligvarer, og finne totalsummen for alle transaksjonene. Den vil så fylle alle disse inn på riktig sted i google sheets regnearket, før den sletter .csv filen.

# Installasjon
For at programmet skal fungere for deg er det noen steg du må gjøre:
### 1. Laste ned playwright med chromium
Dette vil laste ned playwright og de tilhørende nettleserne:
```
pip install playwright
playwright install
```
### 2. Sette opp gspread
Gspread er et python-bibliotek som gjør at du kan skrive kode som samhandler med et google sheets regneark.
Installer gspread:
```
pip install gspread
```
Følg deretter instruksene [her](https://docs.gspread.org/en/v6.1.3/oauth2.html) for å sette opp APIen som brukes, og gi bot-en tilgang til ditt google sheets regneark.
### 3. Kopier sheets malen til din Google Drive
Her er link til malen for regnskapet som jeg har laget: [Google Sheets](https://docs.google.com/spreadsheets/d/1opvIVi0e8IcU82C9tmGcTsCnpDHhUvrDQK3PSP-cn6g/edit?usp=sharing)
Kopier denne til din egen disk. Malen er satt opp slik at det er et ark per år. Programmet vil finne det korrekte arket automatisk, så lenge det er et ark som har det året som navn.
Hvis du endrer på plasseringen til noen av feltene må du også endre hvor programmet skriver i bunnen av koden.

### 3. Tilpasse koden
Det er noen ting du **må** skrive i koden. Alle ligger øverst i koden, under VARIABLER SOM MÅ DEFINERES AV BRUKER. Disse er: `nedlastingsmappe` variablen må inneholde filstien til nedlastingsmappen din. `kontonavn` variablen må inneholde en streng med navnet på kontoen slik den vises i handelsbanken, slik at playwright kan trykke på riktig konto. Den enkleste måten å gjøre dette på er nok å bruke playwright codegen, logge inn i handelsbanken og se hva som ligger inni `page.get_by_text(<DITT KONTONAVN>).click()` som dukker opp. Hvis det er andre ting som ikke fungerer for deg, kan det være du må generere deler av koden selv med playwright codegen. Dette er heldigvis ganske enkelt og intuitivt, det ligger flere gode tutorials på youtube. `sheets_navn` må inneholde en streng med navnet på din Google Sheets, slik at boten kan finne den og åpne den.
Det er valgfritt å endre/legge til elementer i kategoriene, dette gjøres ved å endre på listene som også ligger på toppen av koden.



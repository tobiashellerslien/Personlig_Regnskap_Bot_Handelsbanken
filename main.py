import csv
import os
import gspread
from datetime import datetime
import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time

#!-----------------------VARIABLER SOM MÅ DEFINERES AV BRUKER-----------------------
#Nedlastingsmappe
nedlastingsmappe = r"C:\Users\<DIN_BRUKER>\Downloads" #Endre til din egen nedlastingsmappe

#Kontonavn til Playwright
kontonavn = "Brukskonto fordel ung xxxx xx" #Endre til ditt eget kontonavn slik det vises i handelsbanken, evt. bruk playwright codegen og se hva som kommer når du trykker på kontoen

#Navn på din Google Sheets
sheets_navn = "Personlig Økonomi" #Endre til ditt eget navn på Google Sheets

#Kategorier for budsjettet
daglivarer = ['EXTRA', 'BUNNPRIS', 'KIWI', 'REMA', 'OBS', 'JOKER'] #Legg til flere dagligvarebutikker hvis du vil
transport = ['AtB', 'Ryde'] #Legg til flere transportkategorier hvis du vil
skip = [] #Transaksjoner som inneholder disse ordene i beskrivelser vil bli ignorert, legg til hvis du vil
#!----------------------------------------------------------------------------------

#Finner nåværende datoer
current_datetime = datetime.now()
current_date = current_datetime.day
current_month = current_datetime.month
current_year = current_datetime.year

#--------------------------- Bruker velger måned og år ----------------------------
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
print("Personlig-Økonomi-Bot")
while True:

    print('')
    while True: #velg måned
        month = input("Skriv hvilken måned du vil føre inn (MM), eller trykk enter for å velge nåværende måned: ")
        if not month.isnumeric() and month != '':
            print("Feil format, prøv igjen")
        elif month != '' and (int(month) < 1 or int(month) > 12):
            print("Feil format, prøv igjen")
        else:
            break
    if month == '':
        month = current_month
    else:
        month = int(month)

    print('')

    while True: #velg år
        year = input("Skriv hvilket år (YYYY), eller trykk enter for å velge nåværende år: ")
        if not year.isnumeric() and year != '':
            print("Feil format, prøv igjen")
        elif year != '' and (int(year) < 2024 or int(year) > 2028):
            print("Feil format, prøv igjen")
        else:
            break
    if year == '':
        year = current_year
    else: 
        year = int(year)
    
    if (month > current_month and year >= current_year) or year > current_year:
        print("Du har valgt en fremtidig måned, prøv igjen")
    else:
        confirm = input(f'\nMåned: {month} \nÅr: {year} \nTrykk enter for å bekrefte, skriv noe og trykk enter for å endre: ')
        if confirm == '':
            break

# ----------- Gjør om måned og år til datoer som velges av playwright --------------

if month == current_month and year == current_year:
    end_day = current_date
else:
    end_day = days_in_month[month - 1]

if month < 10:
    month_string = '0' + str(month)
else:
    month_string = str(month)
if end_day < 10:
    end_day_string = '0' + str(end_day)
else:
    end_day_string = str(end_day)

start_date = '01.' + month_string + '.' + str(year)
end_date = end_day_string + '.' + month_string + '.' + str(year)

# ----------------------------------------------------------------------------------

# ------------------------------ PLAYWRIGHT --------------------------------

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.goto("https://www.handelsbanken.no/no/")
    page.get_by_test_id("CookieConsent__declineButton").click()
    page.locator("[data-test-id=\"shb-sepu-header__login-button\"]").click()
    page.get_by_role("link", name="Nettbank").click()
    page.locator("[data-test=\"NO-BANKID\"]").get_by_role("link", name="BankID").click()
    page.get_by_label("Fødselsnummer").click()
    #BANK ID
    page.get_by_text("Brukskontoer").wait_for(state="visible")
    page.get_by_text(kontonavn).click()
    page.get_by_role("link", name="Kontobevegelser").click()
    page.locator("ebank-form-field").filter(has_text="Dato fradd.mm.åååå Velg").get_by_role("textbox").click()
    page.locator("ebank-form-field").filter(has_text="Dato fradd.mm.åååå Velg").get_by_role("textbox").fill(start_date)
    page.locator("ebank-form-field").filter(has_text="Dato tildd.mm.åååå Velg").get_by_role("textbox").click()
    page.locator("ebank-form-field").filter(has_text="Dato tildd.mm.åååå Velg").get_by_role("textbox").fill(end_date)
    time.sleep(2)
    page.get_by_role("button", name="Vis resultat").click()
    page.get_by_label("Eksporter transaksjoner").click()
    with page.expect_download() as download_info:
        page.get_by_role("option", name="CSV").click()
    download = download_info.value
    filnavn = download.suggested_filename
    full_filsti = os.path.join(nedlastingsmappe, filnavn)
    download.save_as(full_filsti)

    # ---------------------
    context.close()
    browser.close()

    return full_filsti


with sync_playwright() as playwright:
    csv_filsti = run(playwright)

#-----------------------------------------------------------------------------------

#Fikser format til streng
def fix_string(string):
    return string.replace(",", ".").replace(" ", "").replace("\u00A0", "")

def category(kategori, beskrivelse, price):
    temp_sum = 0
    for i in kategori:
            if i in beskrivelse:
                temp_sum += price
                break
    return temp_sum

# ---------------------- Åpner og leser filen ------------------------
with open(csv_filsti, 'r') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    next(csv_reader)

    sum_inn = 0
    sum_ut = 0
    sum_dagligvarer = 0
    sum_transport = 0

    for row in csv_reader:

        beløp_inn = 0
        beløp_ut = 0

        dato = row[0]
        if dato == '':
            break

        beskrivelse = row[3]
        if any(i in beskrivelse for i in skip):
            continue

        if row[10] != '':
            beløp_inn = float(fix_string(row[10]))

        if row[11] != '':
            beløp_ut = float(fix_string(row[11]))

        sum_dagligvarer -= category(daglivarer, beskrivelse, beløp_ut)
        sum_transport -= category(transport, beskrivelse, beløp_ut)

        sum_inn += beløp_inn
        sum_ut -= beløp_ut
    
    sum = round(sum_inn - sum_ut, 2)
    sum_inn = round(sum_inn, 2)
    sum_ut = round(sum_ut, 2)
    sum_dagligvarer = round(sum_dagligvarer, 2)
    sum_transport = round(sum_transport, 2)

    print('\nCSV fil lastet ned og lest')
    
# ----------------------------------------------------------------------------------

# --------------------------- Legger inn i sheets ----------------------------------
gc = gspread.service_account()
sh = gc.open(sheets_navn)
print('\nBot har åpnet Google Sheet')

#Velg sheet etter år
wsh = sh.worksheet(str(year))

#Legger inn verdier i riktige celler
month_index = month + 3
wsh.update_cell(month_index, 3, sum_dagligvarer) #dagligvarer
wsh.update_cell(month_index, 4, sum_transport) #transport
wsh.update_cell(month_index, 6, sum_inn) #inn
wsh.update_cell(month_index, 7, sum_ut) #ut
wsh.update_cell(month_index, 8, sum) #sum
print("Bot har lagt inn verdier")

os.remove(csv_filsti) #sletter fil etter bruk
print("CSV fil slettet")
input("\nFerdig! Trykk enter for å lukke programmet")
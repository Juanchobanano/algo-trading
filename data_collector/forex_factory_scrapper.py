from bs4 import BeautifulSoup
import requests
import datetime
import csv
import pandas as pd
import MySQLdb as msql

# Initialize mysql.
use_msql = True
if use_msql:
    try:
        db = msql.connect(host="localhost", user="root", passwd="", db="forex_data")
        tocsv = False
        c = db.cursor()
        print("MYSQL connection established!")
    
    except msql.Error:
        db = None
        print("MYSQL connection failed !")
        print("Closing script...")
        exit

# Define getCalendarioEconomico function.
def getCalendarioEconomico(enlace_inicial,enlace_final):
    
    # convertir en formato de texto y aplicar beautifulsoup
    URLbase = "https://www.forexfactory.com/"
    r = requests.get(URLbase + enlace_inicial)
    data = r.text
    soup = BeautifulSoup(data, "lxml")

    # conseguir los datos de la tabla
    table = soup.find("table", class_="calendar__table")

    # seleccionar cada linea de la tabla y definir los campos a llenar
    trs = table.select("tr.calendar__row.calendar_row")
    campos = ["date","time","currency","impact","event","actual","forecast","previous"]

    
    curr_year = enlace_inicial[-4:]
    curr_date = ""
    curr_time = ""
    
    records = []
    #print("a")
    for tr in trs:

        # cuando se presenta un campo vacío pasa al except y lo escribe en errores
        
        try:
            for campo in campos:
                data = tr.select("td.calendar__cell.calendar__{}.{}".format(campo,campo))[0]
                # print(data)
                if campo=="date" and data.text.strip()!="":
                    curr_date = data.text.strip()
                elif campo=="time" and data.text.strip()!="":
                    # cuando a veces el time es "All Day" o "Day X" por defecto coloco 12:00 am
                    if data.text.strip().find("Day")!=-1:
                        curr_time = "12:00am"
                    else:
                        curr_time = data.text.strip()
                elif campo=="currency":
                    currency = data.text.strip()
                elif campo=="impact":
                    impact = data.find("span")["title"]
                elif campo=="event":
                    event = data.text.strip()
                elif campo=="actual":
                    actual = data.text.strip()
                elif campo=="forecast":
                    forecast = data.text.strip()
                elif campo=="previous":
                    previous = data.text.strip()
                                  

            dt = datetime.datetime.strptime(",".join([curr_year,curr_date,curr_time]),
                                            "%Y,%a%b %d,%I:%M%p")
            
            values = ",".join([str(dt),currency,impact,event,actual,forecast,previous])
            print(values)
            
            try:
                query = "INSERT INTO " + "forex_factory" + " (date_time, currency, impact, name, actual, forecast, previous) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = tuple([dt, currency, impact, event, actual, forecast, previous])
                c.execute(query, values)
                db.commit()
                print(c.rowcount, " record inserted.")
                
            except c.Error as e: 
                print("ERROR: Data couldnt be saved in DB...", e)


            records.append(str(dt),currency,impact,event,actual,forecast,previous)
            with open("forex_calendar.csv", "a") as fc:
                csv.writer(fc).writerow([str(dt),currency,impact,event,actual,forecast,previous])                
                

        except:
            with open("errores.csv","a") as f:
                csv.writer(f).writerow([curr_year,curr_date,curr_time])
            

    
    if enlace_inicial == enlace_final:
        print("impresión exitosa")
        df = pd.DataFrame(records, columns=["day_time","currency","impact","event,actual","forecast","previous"])
        df.to_csv("forex_calendar", encoding="utf-8")
        return
        #exit
    else: 
        # consigue el link de la siguiente semana y sigueee
        follow = soup.select("a.calendar__pagination.calendar__pagination--next.next")
        follow = follow[0]["href"]
        getCalendarioEconomico(follow,enlace_final)

# Se elige cuándo iniciar la visualización de los datos y cuándo finalizarla
getCalendarioEconomico("calendar.php?week=dec1.2007","calendar.php?week=dec23.2018")
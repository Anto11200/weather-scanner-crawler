import schedule
import time
import logging
from crawler.crawl import Crawl
from mongodb import Mongodb
from crawler.meteoattuale import MeteoAttuale
from datetime import datetime
from threading import Thread
from accuracy.calculate_accuracy import *
from nomenclatura import *
import sys

# ---------- CONFIGURAZIONE LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

# ---------- CONNESSIONE AL DB ----------
# mongodb = Mongodb("mongodb://root:admin@localhost:27017/")
# mongodb = Mongodb("mongodb://root:admin@siakoo.asuscomm.com:27017/?authMechanism=DEFAULT")

# ---------- CONNESSIONE AL DB CON RETRY ----------
# mongodb_uri = "mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/"
mongodb_uri = "mongodb://foo:mustbeeightchars@load-balancer-docdb-0183b5887cd86ae8.elb.eu-west-1.amazonaws.com:27017/?tls=true&tlsAllowInvalidHostnames=true&directConnection=true"
db = None
max_retries = 20 # Aumenta i tentativi per maggior robustezza
retry_delay = 5  # Secondi di attesa tra i tentativi

for attempt in range(max_retries):
    try:
        logging.info(f"Tentativo di connessione a MongoDB (Tentativo {attempt + 1}/{max_retries})...")
        # Crea l'istanza di Mongodb (che ora crea il client nel __init__)
        mongodb_instance = Mongodb(mongodb_uri)
        db = mongodb_instance.connect()
        # Prova a fare una semplice operazione per verificare la connessione
        db.command('ping') 
        logging.info("Connessione a MongoDB stabilita con successo!")
        break
    except Exception as e:
        logging.error(f"Connessione a MongoDB fallita: {e}")
        if attempt < max_retries - 1:
            logging.info(f"Riprovo tra {retry_delay} secondi...")
            time.sleep(retry_delay)
        else:
            logging.critical("Massimo numero di tentativi di connessione a MongoDB raggiunto. Uscita.")
            sys.exit(1) 

if db is None:
    logging.critical("Impossibile connettersi a MongoDB. Il programma terminerà.")
    sys.exit(1)
    

# ---------- FUNZIONI ----------
def insertTodayDocument(db, citta, api_key):
    meteo_attuale = MeteoAttuale(api_key)
    localita, data, meteo = meteo_attuale.getFormatedWeather(citta)

    if localita:
        for attempt in range(3):
            try:
                db['centralina'].insert_one({'localita': localita, 'data': data, 'orari': []})
                logging.info(f"Documento giornaliero per {citta} creato")
                break
            except Exception as e:
                logging.error(f"Errore nella creazione del documento attuale: {e}")
    else:
        logging.error(f"Località non trovata - Creazione fallita per {citta}")

def insertHourly(db, citta, api_key):
    meteo_attuale = MeteoAttuale(api_key)
    localita, data, meteo = meteo_attuale.getFormatedWeather(citta)
    if localita:
        control = db['centralina'].find_one({'localita': localita, 'data': data})
        if control:
            db['centralina'].update_one({'data': data, 'localita': localita}, {'$push': {'orari': meteo}})
            logging.info(f"Meteo orario per {citta} inserito")
        else:
            db['centralina'].insert_one({'localita': localita, 'data': data, 'orari': []})
            db['centralina'].update_one({'data': data, 'localita': localita}, {'$push': {'orari': meteo}})
            logging.warning(f"Documento giornaliero per {citta} ricreato perché non presente")
            logging.info(f"Meteo orario per {citta} inserito")
    else:
        logging.error(f"Errore nell'inserimento meteo orario per {citta}")

def insertWeekPrevs(db, citta, id_meteoit):
    b3meteo_prevs = Crawl.crawl3BMeteo(citta)
    meteoit_prevs = Crawl.crawlMeteoit(citta, id_meteoit)

    if b3meteo_prevs:
        try:
            db['3bmeteo'].insert_many(b3meteo_prevs)
            logging.info(f"Previsioni 3bmeteo per {citta} inserite")
        except Exception as e:
            logging.error(f"Inserimento previsioni 3bmeteo fallito: {e}")
    else:
        logging.error(f"Nessuna previsione 3bmeteo per {citta}")

    if meteoit_prevs:
        try:
            db['meteoit'].insert_many(meteoit_prevs)
            logging.info(f"Previsioni meteoit per {citta} inserite")
        except Exception as e:
            logging.error(f"Inserimento previsioni meteoit fallito: {e}")
    else:
        logging.error(f"Nessuna previsione meteoit per {citta}")

def WeekPrevsThread(db):
    logging.info("Inizio thread previsioni settimanali")
    Thread(target=insertWeekPrevs, args=(db, "messina", "83048")).start()
    Thread(target=insertWeekPrevs, args=(db, "roma", "58091")).start()
    Thread(target=insertWeekPrevs, args=(db, "milano", "15146")).start()
    Thread(target=insertWeekPrevs, args=(db, "palermo", "82053")).start()
    Thread(target=insertWeekPrevs, args=(db, "torino", "1272")).start()

def todayDocumentThread(db, api_key):
    logging.info("Inizio thread creazione documento giornaliero")
    Thread(target=insertTodayDocument, args=(db, "messina", api_key)).start()
    Thread(target=insertTodayDocument, args=(db, "rome", api_key)).start()
    Thread(target=insertTodayDocument, args=(db, "milan", api_key)).start()
    Thread(target=insertTodayDocument, args=(db, "palermo", api_key)).start()
    Thread(target=insertTodayDocument, args=(db, "turin", api_key)).start()

def insertHourlyThread(db, api_key):
    logging.info("Inizio thread inserimento meteo orario")
    Thread(target=insertHourly, args=(db, "messina", api_key)).start()
    Thread(target=insertHourly, args=(db, "rome", api_key)).start()
    Thread(target=insertHourly, args=(db, "milan", api_key)).start()
    Thread(target=insertHourly, args=(db, "palermo", api_key)).start()
    Thread(target=insertHourly, args=(db, "turin", api_key)).start()

# ---------- API KEY E SCHEDULAZIONE ----------
api_key = "8c70b7cd7daa4b0da61164403233005"

schedule.every().day.at('22:00').do(WeekPrevsThread, db)    # 22:00
schedule.every().day.at('00:01').do(todayDocumentThread, db, api_key)   # 00:01
schedule.every().hour.at(':02').do(insertHourlyThread, db, api_key)     # :02
schedule.every().day.at('23:30').do(calculateAccuracy, db, "3bmeteo")   # 23:30
schedule.every().day.at('23:30').do(calculateAccuracy, db, "meteoit")   # 23:30
schedule.every().day.at('23:40').do(findNewNames, db)   # 23:40

# ---------- AVVIO ----------
if __name__ == "__main__":
    logging.info("Schedulatore avviato. Premi Ctrl+C per interrompere.")
    while True:
        schedule.run_pending()
        time.sleep(1)

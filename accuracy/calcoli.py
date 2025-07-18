from pymongo import MongoClient
from datetime import datetime
from mongodb import Mongodb
from accuracy.utilities import *
import logging

# ---------- CONFIGURAZIONE LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

# Funzione per ottenere i valori associati alla previsione (ora per ora) di un certo giorno, 
# in modo da fare una media e ottere la previsione complessiva della giornata

def getPrevValues(db, servizio, data, citta):
    
    logging.info(f"Tipo di DATA in getPrevValues: {type(data)} - Valore: {data}")
    logging.info(f"SERVIZIO in getPrevValues: {servizio}")
    logging.info(f"CITTA in getPrevValues: {citta}")
    
    res = list(db[servizio].find({"giorno":data, "localita":citta}))
    logging.info(f"Numero di documenti trovati: {len(res)}")
    
    i = 0
    prev = []
    
    for elem in res:
        prev.append([])
        for ora in elem["previsioni"]:
            standard_name = standardizedNames(ora["meteo"])
            prev[i].append(namesInValue(standard_name))
        i +=1
    return prev # prev_val

# Funzione per ottenere i valori associati al meteo attuale (ora per ora) di un certo giorno, 
# in modo da fare una media e ottere il meteo attuale complessivo della giornata

def getActValues(db, data, citta):
    citta = translateItEn(citta, 'en')
    res = list(db["centralina"].find({"$and":[{"data":data + "T00:00:00", "localita":citta}]}))
    meteo_list = []
    
    if(res):
        for orario in res[0]["orari"]:
            standard_name = standardizedNames(orario["meteo"])
            meteo_list.append(namesInValue(standard_name))
        
    return meteo_list

# Funzione che effettua la media dei valori raccolti delle previsioni (per ogni previsione, calcolo la media)
# in modo da ottenere il valore associato alla giornata (invece delle singole ore)

def getAvgPrevs(list_values):
    avg_list = []
    for single_list_of_values in list_values:
        sum = 0
        n = 0
        for single_val in single_list_of_values:
            sum += single_val
            n +=1
        avg_list.append(round(sum/n))
    return avg_list

# Funzione che effettua la media dei valori raccolti per il giorno attuale
# in modo da ottenere il valore associato alla giornata (invece delle singole ore)

def getAvgActual(list_values):
    avg_list = []
    sum = 0
    n = 0
    for single_val in list_values:
        sum += single_val
        n +=1
    avg_list = round(sum/n)
    return avg_list
    
            


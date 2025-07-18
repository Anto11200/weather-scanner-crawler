from datetime import datetime, date
from accuracy.calcoli import *
from math import sqrt
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

# funzione che effettua gli aggiornamenti parziali: la sommatoria delle previsioni per il giorno attuale, per singola città
def partialSum(formula, servizio, citta, db):
    data = date.today().strftime("%Y-%m-%d")
    somma = 0

    # associare al meteo di ogni ora un valore numerico definito
    prev_val = getPrevValues(db, servizio, data, citta)
    actual_weather = getActValues(db, data, citta)
    
    # [🔍] Log raw dei dati letti dal DB
    logging.info(f"[{servizio}] {citta} - prev_val: {prev_val}")
    logging.info(f"[{servizio}] {citta} - actual_weather: {actual_weather}")

    # calcolare la media delle previsioni e il valore medio attuale
    prev_avg_list = getAvgPrevs(prev_val)
    act_avg = getAvgActual(actual_weather)
    
    # [🔍] Log valori medi usati per il calcolo
    logging.info(f"[{servizio}] {citta} - prev_avg_list: {prev_avg_list}")
    logging.info(f"[{servizio}] {citta} - act_avg: {act_avg}")
    
    # controllo se mancano i dati
    if not prev_avg_list or act_avg is None:
        logging.warning(f"Dati insufficienti per {citta} nel servizio {servizio} - salto calcolo")
        return

    increment = len(prev_avg_list)

    if formula == 'mape':
        for val in prev_avg_list:
            if val == act_avg:
                somma += (0.00005 / act_avg)
            else:
                somma += abs(val - act_avg) / act_avg

    elif formula == 'rmse':
        for val in prev_avg_list:
            somma += (val - act_avg) ** 2

    elif formula == 'bias':
        for val in prev_avg_list:
            somma += (val - act_avg)

    elif formula == 'wbias':
        weight = 1
        weight_sum = 0
        for val in prev_avg_list:
            weight_sum += weight
            somma += (val - act_avg) * weight
            weight += 0.3333333
        increment = weight_sum

    # aggiornamento della formula nel DB
    accuracy_formula = db['accuracy'].find_one({'formula': formula, 'servizio': servizio})
    db['accuracy'].update_one(
        {'_id': accuracy_formula['_id']},
        {'$set': {
            'sum': accuracy_formula['sum'] + somma,
            'n': accuracy_formula['n'] + increment
        }}
    )
    logging.info(f"Aggiornata formula {formula} per {citta} con incremento {increment} e somma {somma:.4f}")


def calculateAccuracy(db, servizio):
    logging.info("Inizio calcolo accuratezza per il servizio: %s", servizio)

    cities = list(db['cities'].find({}, {'_id': 0, 'name': 1}))
    formulas = list(db['accuracy'].distinct("formula"))

    for formula in formulas:
        logging.info(f"Calcolo partialSum per servizio '{servizio}' e formula '{formula}'")
        for city in cities:
            partialSum(formula, servizio, city['name'], db)

        logging.info(f"Calcolo valore complessivo per formula '{formula}'")

        accuracy = db['accuracy'].find_one({'formula': formula, 'servizio': servizio})

        if formula == 'mape':
            mape = round((accuracy['sum'] / accuracy['n']) * 100)
            db['accuracy'].update_one({'_id': accuracy['_id']}, {'$set': {'mape': mape}})
            logging.info(f"MAPE calcolato per {servizio}: {mape}")

        elif formula == 'rmse':
            rmse = round(sqrt(accuracy['sum'] / accuracy['n']), 3)
            db['accuracy'].update_one({'_id': accuracy['_id']}, {'$set': {'rmse': rmse}})
            logging.info(f"RMSE calcolato per {servizio}: {rmse}")

        elif formula == 'bias':
            bias = round(accuracy['sum'] / accuracy['n'], 3)
            db['accuracy'].update_one({'_id': accuracy['_id']}, {'$set': {'bias': bias}})
            logging.info(f"Bias calcolato per {servizio}: {bias}")

        elif formula == 'wbias':
            wbias = round(accuracy['sum'] / accuracy['n'], 3)
            db['accuracy'].update_one({'_id': accuracy['_id']}, {'$set': {'wbias': wbias}})
            logging.info(f"Wbias calcolato per {servizio}: {wbias}")

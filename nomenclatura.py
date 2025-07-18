from mongodb import Mongodb
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

# Restituicse una lista delle nomenclature dei vari servizi meteo non utilizzati all'interno dell'applicazione (questi dovranno poi essere aggiunti manualmente nei file specifici)

def findNewNames(db):
    logging.info("[findNewNames] Funzione avviata.")

    nomi = {}
    try:
        nomi['3bmeteo'] = list(db['3bmeteo'].distinct("previsioni.meteo"))
        logging.info(f"[findNewNames] Nomi trovati in 3bmeteo: {len(nomi['3bmeteo'])}")
        nomi['meteoit'] = list(db['meteoit'].distinct("previsioni.meteo"))
        logging.info(f"[findNewNames] Nomi trovati in meteoit: {len(nomi['meteoit'])}")
        nomi['centralina'] = list(db['centralina'].distinct("orari.meteo"))
        logging.info(f"[findNewNames] Nomi trovati in centralina: {len(nomi['centralina'])}")
    except Exception as e:
        logging.error(f"[findNewNames] Errore durante il recupero dei nomi: {e}")
        return
    
    dizionario = {"sereno":["sereno", "sereno con lievi velature", "sereno o poco nuvoloso", "sereno con foschia",  "prevalentemente soleggiato", "soleggiato", "sereno notte", "Sunny", "Clear"],
                    "velature": ["velature estese", "velature sparse", "velature lievi",],
                    "nubi sparse": ["nubi sparse", "nubi sparse con ampie schiarite", "nubi basse", "nubi basse e schiarite" ], 
                    "parzialmente nuvoloso":["Partly Cloudy", "poco o parzialmente nuvoloso per velature sparse", "poco nuvoloso", "Partly cloudy", "parz nuvoloso"],
                    "nuvoloso": ["nuvoloso con locali aperture", "nuvoloso per velature estese", "cielo in gran parte nuvoloso", "Cloudy", "molto nuvoloso", "nuvoloso"],
                    "coperto": ["coperto", "molto nuvoloso o coperto per nubi alte", "nuvoloso o molto nuvoloso", "molto nuvoloso o coperto", "cielo grigio per nubi basse", "cielo coperto", "Overcast", "coperto per nubi alte", "Mist"],
                    "pioggia debole": ["Thundery outbreaks in nearby", "Patchy rain nearby", "nubi sparse con pioggia debole", "coperto con pioviggini", "coperto con pioggia debole", "nubi sparse con possibili piogge", "coperto con possibili piogge", "coperto con possibili piogge e nebbia", "nubi sparse con pioviggine", "pioggia debole", "nuvoloso con pioggia leggera", "Patchy rain possible", "Light rain", "Patchy light rain", "Light freezing rain", "Light rain shower", "Patchy light drizzle", "Light drizzle", "Freezing drizzle", "Heavy freezing drizzle", "pioggia debole e schiarite", "pioviggine", "pioviggine e schiarite", "possibili piogge"],
                    "pioggia": ["nuvoloso con pioggia media", "coperto con pioggia", "coperto con pioggia e nebbia", "coperto con rovesci di pioggia e nebbia", "pioggia moderata", "Moderate rain at times", "Moderate rain", "Moderate or heavy freezing rain", "Moderate or heavy rain shower", "nubi sparse e rovesci", "pioggia", "pioggia e schiarite", "rovesci di pioggia"],
                    "pioggia forte": ["pioggia forte e schiarite", "coperto con rovesci di pioggia", "piogge di forte intensità", "piogge molto forti, localmente alluvionali", "nubi irregolari con pioggia forte", "nubi irregolari con pioggia molto forte", "pioggia forte", "nuvoloso con pioggia forte", "Heavy rain at times", "Heavy rain", "Torrential rain shower"],
                    "temporale": ["temporale forte e schiarite", "possibili temporali", "temporali forti con grandine", "temporali di forte intensità", "molto nuvoloso con piogge e temporali", "temporali di forte intensità e nebbia", "nubi irregolari con temporali", "molto nuvoloso con piogge e temporali e nebbia", "nubi irregolari con possibile temporale", "nubi irregolari con possibili temporali e nebbia", "nubi irregolari con temporale forte", "temporale", "nuvoloso con temporale", "Patchy light rain with thunder", "Moderate or heavy rain with thunder", "Thundery outbreaks possible", "nubi sparse e temporali"],
                    "nebbia": ["nebbia", "nebbia a banchi"]}

    names = []
    for k, v in dizionario.items():
        names = names + v

    toAdd = []
    for fonte in ['3bmeteo', 'meteoit', 'centralina']:
        for nome in nomi[fonte]:
            if nome not in names:
                toAdd.append(nome)
                logging.warning(f"[findNewNames] '{nome}' da {fonte} non è nel dizionario.")

    try:
        with open("aggiungere_dizionario_nomi.txt", "w") as file:
            for n in toAdd:
                file.write(n + "\n")
        logging.info(f"[findNewNames] Scritti {len(toAdd)} nomi nuovi nel file 'aggiungere_dizionario_nomi.txt'.")
    except Exception as e:
        logging.error(f"[findNewNames] Errore nella scrittura del file: {e}")
        return

    logging.info(f"[findNewNames] Completato. Nomi nuovi: {toAdd}")

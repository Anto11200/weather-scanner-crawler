from pprint import pprint
from datetime import date, timedelta, datetime
from crawler.b3meteo import B3Meteo
from crawler.meteoit import Meteoit

# classe statica per effettuare il crawling complessivo delle previsioni settimanali;

class Crawl:

    # metodo che aggrega i dati ottenuti tramite getTempMaxMin(), e ciascuna previsione giornaliera ora per ora, impostando localita e timestamp;
    # in questo modo si ottiene un documento avente i campi:
    # {
        # 'giorno': giorno a cui fa riferimento la previsione,
        # 'previsioni': array contenente ciascuna ora della giornata e relativi dati (ora, meteo, temperatura, precipitazioni, vento, umidità),
        # 'localita': cità cui fa riferimento la previsione,
        # 'min': minima del giorno,
        # 'max': massima del giorno
    # }

    @staticmethod
    def aggregateData(max_min, prev, localita, prev_6_days):
        for elem in max_min:
            if elem['giorno'] == prev['giorno']:
                prev.update({'localita': localita,
                                'timestamp': datetime.now().isoformat(),
                                'min': elem['min'],
                                'max' : elem['max'],
                            })
                prev_6_days.append(prev)

    # metodo che effettua lo scraping complessivo per 3BMeteo, richiamando una volta getTempMaxMin() e getDayPrev() per 7 volte 
    # (ottenendo le previsioni dei 6 giorni successivi ad oggi), richiamando ogni volta aggregateData() per formattare il dizionario completo

    @staticmethod
    def crawl3BMeteo(localita):
        url = "https://www.3bmeteo.com/meteo/" + localita
        b3meteo = B3Meteo(url)
        max_min = b3meteo.getTempMaxMin()
        prev_6_days = []
    
        for i in range(1, 7):
            url_prev = url + "/dettagli_orari/" + str(i)
            b3meteo = B3Meteo(url_prev)
            prev = b3meteo.getDayPrev()
            if prev is None:
                continue
            else:
                Crawl.aggregateData(max_min, prev, localita, prev_6_days)
        # pprint(prev_6_days)
        return prev_6_days
    
    # metodo che effettua lo scraping complessivo per Meteoit, richiamando una volta getTempMaxMin() e getDayPrev() per 6 volte 
    # (ottenendo le previsioni dei 6 giorni successivi ad oggi), richiamando ogni volta aggregateData() per formattare il dizionario completo
    
    @staticmethod
    def crawlMeteoit(citta, id):
        url = "https://www.meteo.it/meteo/"
        meteoit = Meteoit(url + citta + "-" + id)
        max_min = meteoit.getTempMaxMin()
        prev_6_days = []

        for i in range(1,7):
            if i == 1:
                url_prev = url + citta + "-domani-" + id
            else:
                url_prev = url + citta + "-" + str(i) + "-giorni-" + id
            # print(url_prev)
            meteoit = Meteoit(url_prev)
            prev = meteoit.getDayPrev()
            Crawl.aggregateData(max_min, prev, citta, prev_6_days)
        # pprint(len(prev_6_days))
        return(prev_6_days)


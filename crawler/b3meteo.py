from crawler.paginameteo import Paginameteo
from datetime import date, timedelta, datetime
from pprint import pprint

# classe che eredita da Paginameteo relativa al servizio 3BMeteo;
# il costruttore prende in ingresso l'url della pagina, e tramite setPage() essa viene recuperata come oggetto beautifulsoup;

class B3Meteo(Paginameteo):
    def __init__(self, url) -> None:
        self.setUrl(url)
        self.setPage()

    # metodo per effettuare lo scraping delle massime e minime di ogni giorno;
    # formatto il dizionario contenente i dati ottenuti
    
    def getTempMaxMin(self):
        page = self.getPage()
        nav_days = page.find_all('div', class_= 'navDays', limit= 7)
        days = []
        i = 1
        for day in nav_days[1:]:
            min_max = day.find_all('span', class_='switchcelsius')
            days.append({'giorno': (date.today() + timedelta(days=i)).isoformat(), 
                         'min': min_max[0].text,
                         'max': min_max[1].text,
                        })
            i+=1
        # pprint(days)
        return days
    
    # metodo per effettuare lo scraping della pagina relativa al dettaglio del singolo giorno
    # formatto il dizionario contenente i dati ottenuti

    def getDayPrev(self):
        page = self.getPage()
        day = int(self.getUrl().split("/")[-1])
        tab = page.find('div', {'class': 'table-previsioni-ora'})
        if tab is None:
            return None
        else:
            prev = tab.find_all('div', {'class': 'col-xs-2-4'})
            temp = tab.find_all('span', {'class' : 'switchcelsius'})
            precip = tab.find_all('div', {'class': 'altriDati-precipitazioni'})[1:]
            vento = tab.find_all('span', {'class':'switchkm'})
            umidita = tab.find_all('div', {'class': 'altriDati-umidita'})[1:]
            

            day_prev = {'giorno': (date.today() + timedelta(days=day)).isoformat(),
                    'previsioni': []}
            for i in range(len(prev)):
                day_prev['previsioni'].append({'ora': str(i).rjust(2, "0") + ":00", 
                                                'meteo': prev[i].text.replace("\n", "").strip(), 
                                                'temp': temp[i].text, 
                                                'precip': precip[i].text.replace("\n", "").strip(), 
                                                'vento': vento[i].text, 
                                                'umidita': umidita[i].text.strip()
                                            })
                # pprint(day_prev)
        return day_prev



    
        
    
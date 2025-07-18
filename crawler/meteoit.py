from crawler.paginameteo import Paginameteo
from datetime import date, timedelta
from pprint import pprint

# classe che eredita da Paginameteo relativa al servizio Meteo.it;
# il costruttore prende in ingresso l'url della pagina, e tramite setPage() essa viene recuperata come oggetto beautifulsoup;

class Meteoit(Paginameteo):
    def __init__(self, url) -> None:
        super().__init__()
        self.setUrl(url)
        self.setPage()
    
    # metodo per effettuare lo scraping delle massime e minime di ogni giorno;
    # formatto il dizionario contenente i dati ottenuti
        
    def getTempMaxMin(self):
        page = self.getPage()
        all_temps = page.find_all("div", {"class", "rowTemperature"})
        formated_temps = []
        i=1
      
        for temp in all_temps[1:]:
            actual_temp = temp.find_all('span', {'class':"temperature"})
            formated_temps.append({'giorno': (date.today() + timedelta(days=i)).isoformat(), 
                                   "min": actual_temp[0].text, 
                                   "max": actual_temp[1].text})
            i+=1
        
        return formated_temps
    
    # metodo per effettuare lo scraping della pagina relativa al dettaglio del singolo giorno
    # formatto il dizionario contenente i dati ottenuti

    def getDayPrev(self):
        page = self.getPage()
        list_temp_spans = page.find_all("span", {"class": "replacedH5Temperature"})
        list_container_hum_vent = page.find_all("div", {"class": "containerEndingInfo"})
        list_central_info = page.find_all("div", {"class": "rowCentralInfo"})
        list_downfall = page.find_all("p", {"class":"downfallText"})
        list_winds = []
        list_rain = []
        string_day = self.getUrl().split("-")
        dayprev = {'giorno': '', 'previsioni':[]}
        
        #controlla se è presente del testo, se il controllo da false allora appende assenti alla 
        # lista altrimenti.
        # operazione di split per prendere i dati relativi alla pioggia
        
        for rain in list_downfall:
            if(rain.text):
                list_rain.append(rain.text.split("(")[1].split("-")[0].rstrip())
            else:
                list_rain.append("assenti")
        
        if(string_day[1] == "domani"):
            dayprev["giorno"] = (date.today() + timedelta(days=1)).isoformat()
        else:
            dayprev["giorno"] = (date.today() + timedelta(days=int(string_day[1]))).isoformat()
        
        for cont_vent in list_container_hum_vent:
            temp_vent = cont_vent.find("p", {"class":"windInfoContainer"}).find("span").find_all("span")
            list_winds.append(round((int(temp_vent[0].text) + int(temp_vent[1].text))/2))
        
        
        for i in range(0, len(list_temp_spans)-1):
            dayprev["previsioni"].append({"ora":str(i).rjust(2,"0") + ":00",
                                          "meteo":list_central_info[i].find("img")["alt"], 
                                          "temp": list_temp_spans[i].text,
                                          "precip":list_rain[i],
                                          "vento": list_winds[i], 
                                          "umidita": list_container_hum_vent[i].find("span", 
                                                                    {"style": "margin-left:10px"}).text})
            
        return dayprev
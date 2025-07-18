from datetime import datetime
import requests
import json
import time

#Classe che permette di ottenere le previsione dell'ora attuale attraverso il servizio di API weatherapi.com
#Il costruttore setta l'url base delle api e l'api key del servizio

class MeteoAttuale:
    def __init__(self, api_key) -> None:
        self.setApiKey(api_key)
        self.base_url = "http://api.weatherapi.com/v1/"
        
    def setApiKey(self, api_key):
        self.api_key = api_key
    
    def getApiKey(self):
        return self.api_key

    def getBaseUrl(self):
        return self.base_url
    
    #Permette di ottenere il meteo attuale di una città
    #Con type indico se voglio il meteo corrente oppure la previsione dei giorni successivi 
    # (consultare la docum. weatherapi), il parametro aqi permette di ottenere le condizioni 
    # riguardo l'aria, di default è impostato a no

    def getWeather(self, city, type="current.json", aqi="no"):
        url = self.getBaseUrl() + type + "?key=" + self.getApiKey() + "&q=" + city + "&aqi=" + aqi
        attempt = 0
        response = ""
        while attempt < 3 and response == "":
            try:
                f = open("log.txt", "a")
                f.write("[INFO] " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + f" Tentativo di connessione n. {attempt} all'url {url}\n")
                f.close()
                response = json.loads(requests.get(url).text)
            except Exception as e:
                f = open("log.txt", "a")
                f.write("[ERRORE] " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + " Errore nella connessione alle api\n[ERRORE]" + str(e) + "\n")
                f.close()
                attempt +=1
                time.sleep(180)
            
        return response
    
    #Permette di formattare le informazioni ottenute dalla funzione getWeather in modo da avere uno standard per quando 
    # le informazioni verranno inserite nel db
    
    def getFormatedWeather(self, city, type="current.json", aqi="no"):
        weather = self.getWeather(city, type, aqi)
        if weather != "":
            data_ora = weather['location']['localtime'].split(" ")
            
            return city, datetime.strptime(data_ora[0], '%Y-%m-%d').isoformat(), {"ora": data_ora[1].rjust(5, "0"), 
                    "meteo": weather["current"]["condition"]["text"], 
                    "temp": weather["current"]["temp_c"], 
                    "precip": str(weather["current"]["precip_mm"]) + "mm", 
                    "vento": weather["current"]["wind_kph"], 
                    "umidita": str(weather["current"]["humidity"]) + "%"
                    }
        return (None, None, None)
        
        
from abc import ABC, abstractmethod
import bs4, requests
import time
from datetime import datetime

# classe astratta per ottenere la pagina di cui effettuare lo scraping, ottenendola tramite BeautifulSoup;
# vengono definiti i metodi getter e setter relativi a pagina e relativo url;
# infinem vengono definiti i metodi astratti getTempMaxMin() e getDayPrev() per ottenere temperature massime e minime e previsioni.
# sono metodi astratti in quanto verrano implementati dalle classi B3Meteo e Meteoit che ereditano da Paginameteo.

class Paginameteo:
    
    def setPage(self):
        url = self.getUrl()
        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        attempt = 0
        sent= False
        while attempt < 3 and sent == False:
            try:
                f = open("log.txt", "a")
                f.write("[INFO] " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + f" previsioni tentativo di connessione: {url}\n")
                f.close()
                response = requests.get(url, headers=headers)       #funzione get permette di ottenere la pagina richiesta, salvata in response
                response.raise_for_status() #solleva eccezione in caso di errore
                sent = True
            except Exception as e:
                f = open("log.txt", "a")
                f.write("[ERRORE] " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + f" Errore nella connessione con {url}\n[ERRORE]" + str(e) + "\n")
                f.close()
                attempt +=1
                time.sleep(180)
                
        self.page = bs4.BeautifulSoup(response.text, 'html.parser')
        
    def getPage(self):
        return self.page
        
    def setUrl(self, url):
        self.url = url
    
    def getUrl(self):
        return self.url
    
    @abstractmethod
    def getTempMaxMin():
        pass
    
    @abstractmethod
    def getDayPrev():
        pass
    
    
    
    
    
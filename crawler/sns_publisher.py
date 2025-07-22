import boto3
import logging
import os

# ---------- CONFIGURAZIONE LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)


def get_sns_client():
    """
    Inizializza e restituisce un client Boto3 per SNS.
    Utilizza variabili d'ambiente per le credenziali AWS e la regione per sicurezza.
    """
    aws_region = "us-east-1"

    try:
        # Per produzione, evita di passare direttamente le credenziali qui.
        # Boto3 le cercherà automaticamente in variabili d'ambiente, file di credenziali AWS, o ruoli IAM.
        sns_client = boto3.client('sns', region_name=aws_region)
        return sns_client
    except Exception as e:
        logging.info(f"Errore durante l'inizializzazione del client SNS: {e}")
        raise # Rilancia l'eccezione per fermare l'esecuzione se il client non può essere creato


def publish_weather_update(message_body: str = "Le previsioni meteo sono state aggiornate! Visita la nostra app per i dettagli!",
                           subject: str = 'Aggiornamento Previsioni Meteo',
                           topic_arn: str = os.environ.get("SNS_TOPIC", "arn:aws:sns:us-east-1:116695809482:weather-daily-notifications")
                            #topic_arn: str = "arn:aws:sns:us-east-1:116695809482:weather-daily-notifications"
                            ):
    """
    Pubblica un messaggio su un topic SNS specifico.

    Args:
        message_body (str): Il corpo principale del messaggio da inviare.
        subject (str): L'oggetto del messaggio (per email). Default: 'Aggiornamento Previsioni Meteo'.
        topic_arn (str): L'ARN del topic SNS a cui pubblicare.
                         Se non fornito, cerca la variabile d'ambiente 'SNS_TOPIC_ARN'.
    """
    
    if topic_arn is None:
        raise ValueError("SNS_TOPIC_ARN non specificato e non trovato nelle variabili d'ambiente.")

    sns_client = get_sns_client()

    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message_body,
            Subject=subject
        )
        logging.info(f"Messaggio SNS pubblicato con ID: {response['MessageId']}")
        return response
    except Exception as e:
        logging.info(f"Errore nella pubblicazione del messaggio SNS sul topic {topic_arn}: {e}")
        # Puoi decidere se rilanciare l'eccezione o gestirla in modo più elegante
        raise
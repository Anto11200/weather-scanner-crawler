#!/bin/bash

# --- 1. Assicurati che Minikube stia usando l'ambiente Docker corretto ---
# Questo è fondamentale se passi tra il Docker locale e il Docker di Minikube
eval $(minikube docker-env)

# --- 2. Costruisci e pusha la nuova immagine Docker ---
# --no-cache forza la ricostruzione di tutti i layer, assicurando che le modifiche al codice siano incluse
docker build --no-cache -t "antoniolauro/weather:latest" .

docker push "antoniolauro/weather:latest"

# --- 3. Elimina il deployment esistente (per forzare il pull della nuova immagine) ---
# --ignore-not-found=true evita errori se il deployment non esiste ancora
kubectl delete deploy/weather-crawler --ignore-not-found=true

# --- 4. Applica il nuovo deployment a Kubernetes ---
kubectl apply -f "manifests/"
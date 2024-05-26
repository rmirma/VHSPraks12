from flask import Flask
from flask import request
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
import json
import os
import requests

app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})

def blob_konteineri_loomine(konteineri_nimi):
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        blob_service_client.create_container(konteineri_nimi)


def blob_raamatute_nimekiri():
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    raamatud = []
    for blob in container_client.list_blobs():
        raamatud.append(blob.name)
    return raamatud


def blob_alla_laadimine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    return blob_client.download_blob().content_as_text()


def blob_ules_laadimine_sisu(faili_nimi, sisu):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.upload_blob(sisu)


def blob_kustutamine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.delete_blob()


@app.route('/raamatud/', methods=['GET'])
def raamatu_nimekiri():
    raamatud = blob_raamatute_nimekiri()
    return {"raamatud": raamatud}, 200


@app.route('/raamatud/<book_id>', methods=['GET'])
def raamatu_allatombamine(book_id):
    try:
        raamatu_sisu = blob_alla_laadimine(f"{book_id}.txt")
        return (raamatu_sisu, 200, {'Content-Type': 'text/plain; charset=utf-8'})
    except:
        return ({}, 404)


@app.route('/raamatud/<book_id>', methods=['DELETE'])
def raamatu_kustutamine(book_id):
    try:
        blob_kustutamine(f"{book_id}.txt")
        return {}, 204
    except:
        return {}, 404


@app.route('/raamatud/', methods=['POST'])
def raamatu_lisamine():
    # Loeme sisse raamatu ID
    input = json.loads(request.data)
    book_id = input["raamatu_id"]
    # Kontrollime, kas selline raamat on juba olemas
    if f"{book_id}.txt" in blob_raamatute_nimekiri():
        return {"tulemus": "Raamat on juba olemas ", "raamatu_id": book_id}, 409
    # Laeme raamatu Gutenbergi repositooriumist alla
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    tekst = requests.get(url).text
    blob_ules_laadimine_sisu(f"{book_id}.txt", tekst)
    return {"tulemus": "Raamatu loomine õnnestus ", "raamatu_id": book_id}, 201


# Azure Blob konfiguratsioon
blob_connection_string = os.getenv('APPSETTING_AzureWebJobsStorage')
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)

blob_container_name = os.getenv('APPSETTING_blob_container_name')

if __name__ == '__main__':
    app.run(debug=True)

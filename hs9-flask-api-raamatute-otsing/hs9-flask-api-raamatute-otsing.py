from flask import Flask
from flask import request
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
import json
import os

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


@app.route('/raamatu_otsing/<raamatu_id>', methods=['POST'])
def raamatust_sona_otsimine(raamatu_id):
    luger = 0
    # Loeme sisse raamatu ID
    input = json.loads(request.data)
    sone = input["sone"]
    tekst = blob_alla_laadimine(f"{raamatu_id}.txt")
    for rida in tekst.split("\n"):
        sonad = rida.split()
        if sone in sonad:
            luger += 1
    return {"raamatu_id": raamatu_id, "sone": sone, "leitud": luger}, 200


@app.route('/raamatu_otsing', methods=['POST'])
def raamatutest_sona_otsimine():
    sone = json.loads(request.data)["sone"]
    raamatud = blob_raamatute_nimekiri()
    tulemused = []
    for raamatu_id in raamatud:
        tekst = blob_alla_laadimine(f"{raamatu_id}")
        luger = 0
        for rida in tekst.split("\n"):
            sonad = rida.split()
            if sone in sonad:
                luger += 1
        tulemused.append({"raamatu_id": raamatu_id, "leitud": luger})
    return {"sone": sone, "tulemused": tulemused}, 200


blob_connection_string = os.getenv('AZURE_BLOB_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)

blob_container_name = "mirmahs8praks"

if __name__ == '__main__':
    app.run(debug=True)

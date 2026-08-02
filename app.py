from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, uuid, os

app = Flask(__name__)
CORS(app)

COLLECTION_KEY = os.environ.get("COLLECTION_KEY")
DISBURSEMENT_KEY = os.environ.get("DISBURSEMENT_KEY")
TARGET_ENV = "sandbox" # change to "mtnuganda" when you go live

BASE_COLLECTION = "https://proxy.momoapi.mtn.com/collection/v1_0"
BASE_DISBURSEMENT = "https://proxy.momoapi.mtn.com/disbursement/v1_0"

@app.route("/deposit", methods=["POST"])
def deposit():
    data = request.json
    ref_id = str(uuid.uuid4())
    headers = {"X-Reference-Id": ref_id, "X-Target-Environment": TARGET_ENV, "Ocp-Apim-Subscription-Key": COLLECTION_KEY, "Content-Type": "application/json"}
    payload = {"amount": str(data['amount']), "currency": "UGX", "externalId": data['user_id'], "payer": {"partyIdType": "MSISDN", "partyId": data['phone']}, "payerMessage": "ONIKE Deposit", "payeeNote": "Deposit"}
    r = requests.post(f"{BASE_COLLECTION}/requesttopay", json=payload, headers=headers)
    if r.status_code == 202:
        return jsonify({"message": "Prompt sent to your phone. Enter MoMo PIN."})
    return jsonify({"message": "Failed: " + r.text})

@app.route("/withdraw", methods=["POST"])
def withdraw():
    data = request.json
    ref_id = str(uuid.uuid4())
    headers = {"X-Reference-Id": ref_id, "X-Target-Environment": TARGET_ENV, "Ocp-Apim-Subscription-Key": DISBURSEMENT_KEY, "Content-Type": "application/json"}
    payload = {"amount": str(data['amount']), "currency": "UGX", "externalId": data['user_id'], "payee": {"partyIdType": "MSISDN", "partyId": data['phone']}, "payerMessage": "ONIKE Withdraw", "payeeNote": "Withdrawal"}
    r = requests.post(f"{BASE_DISBURSEMENT}/transfer", json=payload, headers=headers)
    if r.status_code == 202:
        return jsonify({"message": "Withdrawal sent. Check your phone."})
    return jsonify({"message": "Failed: " + r.text})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId  # Tambahkan ini


app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017")
db = client["pembukuan_db"]
col = db["pembukuan"]

# POST /api/pembukuan → simpan data baru
@app.route("/api/pembukuan", methods=["POST"])
def simpan_pembukuan():
    try:
        data = request.json
        now = datetime.now()

        data["tanggal"] = now.strftime("%Y-%m-%d")
        data["jam"] = now.strftime("%H:%M:%S")
        data["waktuLengkap"] = now.isoformat()

        col.insert_one(data)
        return jsonify({"message": "Data berhasil disimpan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET /api/riwayat → ambil semua riwayat
@app.route("/api/riwayat", methods=["GET"])
def ambil_riwayat():
    data = list(col.find().sort("waktuLengkap", -1))
    for d in data:
        d["_id"] = str(d["_id"])
    return jsonify(data), 200

@app.route("/api/pembukuan/<id>", methods=["PUT"])
def update_pembukuan(id):
    try:
        new_data = request.json
        col.update_one({"_id": ObjectId(id)}, {"$set": new_data})
        return jsonify({"message": "Data berhasil diupdate"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId  # untuk update data berdasarkan _id
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/docs'  # URL untuk dokumentasi
API_URL = '/swagger.json'  # File JSON spesifikasi

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Dokumentasi API Pembukuan"}
)


# ────────────────────────
# Inisialisasi Flask App
# ────────────────────────
app = Flask(__name__)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
CORS(app)

# ────────────────────────
# Koneksi ke MongoDB
# ────────────────────────
client = MongoClient("mongodb+srv://ferdid047:085778612820Iu%2A@cluster0.bk8p5rr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["pembukuan_db"]
col = db["pembukuan"]


# ────────────────────────
# Simpan Pembukuan Baru
# ────────────────────────
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

# ────────────────────────
# Ambil Riwayat Semua Pembukuan
# ────────────────────────
@app.route("/api/riwayat", methods=["GET"])
def ambil_riwayat():
    data = list(col.find().sort("waktuLengkap", -1))
    for d in data:
        d["_id"] = str(d["_id"])  # konversi ObjectId ke string
    return jsonify(data), 200

# ────────────────────────
# Update Pembukuan berdasarkan ID
# ────────────────────────
@app.route("/api/pembukuan/<id>", methods=["PUT"])
def update_pembukuan(id):
    try:
        data = request.json

        # Tambahkan debug print di sini
        print("DATA MASUK:", data)

        # Validasi: pastikan data ada
        pembukuan = col.find_one({"_id": ObjectId(id)})
        if not pembukuan:
            return jsonify({"error": "Data tidak ditemukan"}), 404

        # Update semua field
        update_data = {
            "saldo": data.get("saldo", {}),
            "penghutang": data.get("penghutang", []),
            "totalHariIni": data.get("totalHariIni"),
            "saldoKemarin": data.get("saldoKemarin"),
            "selisih": data.get("selisih"),
        }

        col.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        return jsonify({"message": "Data berhasil diperbarui"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/swagger.json')
def swagger_spec():
    from flask import send_file
    return send_file('swagger.json')


# ────────────────────────
# Jalankan Aplikasi
# ────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

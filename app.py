import matplotlib
matplotlib.use('Agg')  # Non-interactive backend kullan
from flask import Flask, jsonify, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io


app = Flask(__name__)

# Veri setini yükleme
data = pd.read_excel("realistic_all_veri_seti.xlsx")

# Sulama algoritması
def irrigation_algorithm(row):
    reasons = []
    if row["ToprakNemi(%)"] < 30:
        reasons.append("Düşük Toprak Nemi")
    if row["HavaSicakligi(°C)"] > 30 and row["HavaNemi(%)"] < 40:
        reasons.append("Yüksek Sıcaklık ve Düşük Nem")
    if row["YaprakRengi"] in ["Açık Yeşil", "Kahverengi"]:
        reasons.append("Bitki Stresi (Yaprak Rengi)")
    return "Sulama Gerekli" if reasons else "Sulama Gereksiz", ", ".join(reasons) or None

# Ana sayfa (HTML'yi döner)
@app.route("/")
def home():
    return render_template("index.html")

# Veri setini JSON formatında döner
@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(data.to_dict(orient="records"))

# Toprak nemi grafiğini PNG olarak döner
@app.route("/graph/soil-moisture", methods=["GET"])
def graph_soil_moisture():
    plt.figure(figsize=(10, 5))
    plt.plot(data["TarihSaat"], data["ToprakNemi(%)"], label="Toprak Nemi", color="blue")
    plt.xlabel("Tarih Saat")
    plt.ylabel("Toprak Nemi (%)")
    plt.title("Toprak Nemi Zaman Grafiği")
    plt.legend()

    # PNG olarak döndür
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()
    return send_file(img, mimetype="image/png")

# Sulama algoritmasını çalıştırarak durumu döner
@app.route("/irrigation", methods=["GET"])
def get_irrigation_status():
    results = []
    for _, row in data.iterrows():
        status, reason = irrigation_algorithm(row)
        results.append({
            "TarihSaat": row["TarihSaat"],
            "SulamaDurumu": status,
            "Sebep": reason
        })
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from flask import Flask, jsonify, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
from base64 import b64encode
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# Veri setini yükleme
data = pd.read_excel("realistic_all_veri_seti.xlsx")

# Sulama algoritması
def irrigation_algorithm(row):
    reasons = []
    if row["ToprakNemi(%)"] < 40:
        reasons.append("Düşük Toprak Nemi")
    if row["HavaSicakligi(°C)"] > 30 and row["HavaNemi(%)"] < 40:
        reasons.append("Yüksek Sıcaklık ve Düşük Nem")
    if row["YaprakRengi"] in ["Kahverengi"]:
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

# Grafik oluşturma fonksiyonu
def create_graph(y_data, y_label, title, color):
    plt.figure(figsize=(10, 5))
    plt.plot(data["TarihSaat"], y_data, label=title, color=color)
    plt.xlabel("Tarih Saat")
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()
    return img

# Tüm Grafiklerin HTML'de Gösterimi
@app.route("/graph/all", methods=["GET"])
def graph_all():
    graphs = {
        "Toprak Nemi": create_graph(data["ToprakNemi(%)"], "Toprak Nemi (%)", "Toprak Nemi Grafiği", "blue"),
        "Hava Sıcaklığı": create_graph(data["HavaSicakligi(°C)"], "Sıcaklık (°C)", "Hava Sıcaklığı Grafiği", "red"),
        "Hava Nemi": create_graph(data["HavaNemi(%)"], "Hava Nemi (%)", "Hava Nemi Grafiği", "green"),
        "Işık Yoğunluğu": create_graph(data["IsikYogunlugu(lux)"], "Işık Yoğunluğu (lux)", "Işık Yoğunluğu Grafiği", "orange")
    }

    # Grafikleri base64 formatına dönüştür
    encoded_graphs = {title: f"data:image/png;base64,{b64encode(img.read()).decode()}" for title, img in graphs.items()}
    return render_template("all_graphs.html", graphs=encoded_graphs)

# Sulama Durumu Endpoint'i
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

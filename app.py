import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from flask import Flask, jsonify, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
from base64 import b64encode
from flask_cors import CORS
import requests
import joblib
from sklearn.preprocessing import StandardScaler
# Modeli ve Scaler'ı Yükle
import pickle

with open("trained_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

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

    # Grafikleri base64 formatına dönüştür ve JSON olarak hazırla
    encoded_graphs = {
        title: f"data:image/png;base64,{b64encode(img.read()).decode()}"
        for title, img in graphs.items()
    }

    # JSON olarak döndür
    return jsonify(encoded_graphs)

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

# Thingspeak API ile veri alma ve modeli entegre etme
@app.route("/thingspeak", methods=["GET"])
def get_thingspeak_data_and_predict():
    try:
        # Thingspeak API URL
        api_url = "https://api.thingspeak.com/channels/2736785/feeds.json?api_key=RE1I0AGF14BCQZLD&results=10"
        response = requests.get(api_url)
        response.raise_for_status()
        thingspeak_data = response.json()

        # Son 10 veriyi formatlama
        formatted_data = [
            {
                "time": feed["created_at"],
                "ToprakNemi(%)": float(feed["field4"]),
                "HavaSicakligi(Â°C)": float(feed["field2"]),
                "HavaNemi(%)": float(feed["field1"]),
                "IsikYogunlugu(lux)": float(feed["field3"]),
            }
            for feed in thingspeak_data.get("feeds", []) if feed["field1"] and feed["field2"] and feed["field3"] and feed["field4"]
        ]

        if len(formatted_data) < 10:
            return jsonify({"status": "error", "message": "Yeterli veri yok (10 veri gerekli)."})

        # Tahmin için veri çerçevesi oluşturma
        test_samples = pd.DataFrame(formatted_data)

        # Özellik adlarını eşitle
        test_samples = test_samples[['ToprakNemi(%)', 'HavaSicakligi(Â°C)', 'HavaNemi(%)', 'IsikYogunlugu(lux)']]
        timestamps = [item["time"] for item in formatted_data]

        # Ölçeklendirme
        test_samples_scaled = scaler.transform(test_samples)

        # Tahmin ve olasılık hesaplama
        predictions = model.predict(test_samples_scaled)
        probabilities = model.predict_proba(test_samples_scaled)[:, 1]  # Sadece "Sulama Gerekli" olasılığı

        # Zaman, tahmin ve olasılık sonuçlarını formatla
        prediction_results = [
            {
                "time": timestamps[idx],
                "SulamaDurumu": "Sulama Gerekli" if predictions[idx] == 1 else "Sulama Gereksiz",
                "Probability": round(probabilities[idx] * 100, 2)  # Yüzdelik formatta olasılık
            }
            for idx in range(len(predictions))
        ]

        return jsonify({"status": "success", "predictions": prediction_results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})




if __name__ == "__main__":
    app.run(debug=True)

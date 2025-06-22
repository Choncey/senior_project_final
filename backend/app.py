from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.base import BaseEstimator, RegressorMixin

app = Flask(__name__)

# 🔧 Model yükleniyor
with open("boosted_model (1).pkl", "rb") as f:
    model = pickle.load(f)

# 📊 Veri dosyası yükleniyor
df = pd.read_excel("sentetik_veri_kuru_yaz.xlsx")
df["TarihSaat"] = pd.to_datetime(df["TarihSaat"])
df.set_index("TarihSaat", inplace=True)

# 🔮 Su tahmin fonksiyonu
@app.route("/tahmin", methods=["POST"])
def tahmin():
    data = request.get_json()
    try:
        sicaklik = float(data["sicaklik"])
        hava_nemi = float(data["havaNemi"])
        toprak_nemi = float(data["toprakNemi"])
        isik = float(data["isik"])
    except (KeyError, ValueError):
        return jsonify({"error": "Eksik veya hatalı veri girdisi"}), 400

    if toprak_nemi >= 40:
        return jsonify({"sulamaGerekliMi": "Hayır", "suMiktari": 0})
    else:
        x_input = np.array([[sicaklik, hava_nemi, toprak_nemi, isik]])
        su = model.predict(x_input)[0]
        return jsonify({"sulamaGerekliMi": "Evet", "suMiktari": round(su, 2)})

# 📅 Yeni endpoint: 30 günlük tahmin
@app.route("/aylik_sulama_tahmini", methods=["POST"])
def aylik_sulama():
    data = request.get_json()
    try:
        baslangic = datetime.strptime(data["tarih"], "%Y-%m-%d")
        sicaklik = float(data["sicaklik"])
        hava_nemi = float(data["havaNemi"])
        isik = float(data["isik"])
        toprak_nemi = float(data["toprakNemi"])
    except:
        return jsonify({"error": "Eksik veya hatalı veri seti"}), 400

    gun = baslangic
    sulama_gunleri = []
    toplam_su = 0

    for i in range(30):
        # Excel'den tahmini hava verileri çekilir
        try:
            satir = df.loc[gun]
            sicaklik = satir["Sıcaklık (°C)"]
            hava_nemi = satir["Hava Nemi (%)"]
            isik = satir["Işık (lux)"]
        except:
            pass  # Veri yoksa son bilinenler kalır

        if toprak_nemi < 40:
            x_input = np.array([[sicaklik, hava_nemi, toprak_nemi, isik]])
            su_miktari = model.predict(x_input)[0]
            su_miktari = round(su_miktari, 2)
            sulama_gunleri.append({
                "gun": gun.strftime("%Y-%m-%d"),
                "su": su_miktari
            })
            toplam_su += su_miktari
            toprak_nemi = 50  # Sulama yapıldı

        # Nem azalımı simülasyonu
        toprak_nemi -= np.random.uniform(0.4, 1.1)
        toprak_nemi = max(toprak_nemi, 0)
        gun += timedelta(days=1)

    return jsonify({
        "sulamaGunleri": sulama_gunleri,
        "toplamSu": round(toplam_su, 2)
    })
@app.route("/grafik_verisi", methods=["GET"])
def grafik_verisi():
    try:
        df = pd.read_excel("sentetik_veri_kuru_yaz.xlsx")
        df["TarihSaat"] = pd.to_datetime(df["TarihSaat"])
        df = df.sort_values("TarihSaat")
        
        # Sadece gerekli sütunları al ve JSON'a çevir
        df_out = df[["TarihSaat", "Sıcaklık (°C)", "Hava Nemi (%)", "Toprak Nemi (%)", "Işık (lux)"]].copy()
        df_out["TarihSaat"] = df_out["TarihSaat"].dt.strftime('%Y-%m-%d')

        result = df_out.rename(columns={
            "TarihSaat": "tarih",
            "Sıcaklık (°C)": "sicaklik",
            "Hava Nemi (%)": "havaNemi",
            "Toprak Nemi (%)": "toprakNemi",
            "Işık (lux)": "isik"
        })

        return jsonify(result.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": f"Veri işlenirken hata oluştu: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

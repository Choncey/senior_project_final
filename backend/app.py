from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta
import requests
import threading
import time

app = Flask(__name__)

# Model and static dataset load
with open("boosted_model (1).pkl", "rb") as f:
    model = pickle.load(f)

static_df = pd.read_excel("sentetik_veri_kuru_yaz.xlsx")
static_df["TarihSaat"] = pd.to_datetime(static_df["TarihSaat"])
static_df.set_index("TarihSaat", inplace=True)

# Variables to store latest values
dynamic_prediction = {"irrigationNeeded": "No", "waterAmount": 0.0}
dynamic_monthly = {"irrigationDays": [], "totalWater": 0.0}

# Function to get latest sensor values from ThinkSpeak
def fetch_latest_sensor_data():
    try:
        url = "https://api.thingspeak.com/channels/2978511/feeds.json?api_key=0611PKN079UI17Z5&results=1"
        response = requests.get(url).json()["feeds"][0]
        return {
            "temperature": float(response["field1"] or 0),
            "humidity": float(response["field2"] or 0),
            "moisture": float(response["field3"] or 0),
            "light": float(response["field4"] or 0)
        }
    except:
        return None

# Background function to update prediction values
def background_updater():
    global dynamic_prediction, dynamic_monthly
    while True:
        data = fetch_latest_sensor_data()
        if data:
            x_input = np.array([[data["temperature"], data["humidity"], data["moisture"], data["light"]]])
            if data["moisture"] >= 40:
                dynamic_prediction = {"irrigationNeeded": "No", "waterAmount": 0.0}
            else:
                su = model.predict(x_input)[0]
                dynamic_prediction = {"irrigationNeeded": "Yes", "waterAmount": round(su, 2)}

            # Monthly prediction
            gun = datetime.now()
            toprak_nemi = data["moisture"]
            sulama_gunleri = []
            toplam_su = 0
            for i in range(30):
                try:
                    row = static_df.loc[gun]
                    sicaklik = row["Sıcaklık (°C)"]
                    hava_nemi = row["Hava Nemi (%)"]
                    isik = row["Işık (lux)"]
                except:
                    sicaklik = data["temperature"]
                    hava_nemi = data["humidity"]
                    isik = data["light"]

                if toprak_nemi < 40:
                    x_input = np.array([[sicaklik, hava_nemi, toprak_nemi, isik]])
                    su_miktari = model.predict(x_input)[0]
                    su_miktari = round(su_miktari, 2)
                    sulama_gunleri.append({"date": gun.strftime("%Y-%m-%d"), "water": su_miktari})
                    toplam_su += su_miktari
                    toprak_nemi = 50

                ay = gun.month
                if ay in [6, 7, 8]:
                    toprak_nemi -= np.random.uniform(0.8, 1.2)
                elif ay in [12, 1, 2]:
                    toprak_nemi -= np.random.uniform(0.2, 0.4)
                else:
                    toprak_nemi -= np.random.uniform(0.4, 0.7)

                toprak_nemi = max(toprak_nemi, 0)
                gun += timedelta(days=1)

            dynamic_monthly = {"irrigationDays": sulama_gunleri, "totalWater": round(toplam_su, 2)}
        
        time.sleep(15)

# Start background thread
threading.Thread(target=background_updater, daemon=True).start()

@app.route("/get_latest_prediction", methods=["GET"])
def get_latest_prediction():
    return jsonify(dynamic_prediction)

@app.route("/get_monthly_prediction", methods=["GET"])
def get_monthly_prediction():
    return jsonify(dynamic_monthly)

@app.route("/start_irrigation", methods=["POST"])
def start_irrigation():
    data = request.get_json()
    try:
        required_water = float(data["waterAmount"])
    except:
        return jsonify({"error": "Invalid input"}), 400

    requests.get("https://api.thingspeak.com/update?api_key=Z7WE9ZM00EHV7RC9&field1=1")

    accumulated = 0
    while accumulated < required_water:
        resp = requests.get("https://api.thingspeak.com/channels/2978511/feeds.json?api_key=0611PKN079UI17Z5&results=1")
        feed = resp.json()["feeds"][0]
        water = float(feed["field6"] or 0)
        accumulated += water
        if accumulated >= required_water:
            break

    requests.get("https://api.thingspeak.com/update?api_key=Z7WE9ZM00EHV7RC9&field1=0")

    return jsonify({"message": "Irrigation complete", "totalWaterUsed": accumulated})

@app.route("/graph_data", methods=["GET"])
def graph_data():
    try:
        df_graph = pd.read_excel("sentetik_veri_kuru_yaz.xlsx")
        df_graph["TarihSaat"] = pd.to_datetime(df_graph["TarihSaat"])
        df_graph = df_graph.sort_values("TarihSaat")

        df_out = df_graph[["TarihSaat", "Sıcaklık (°C)", "Hava Nemi (%)", "Toprak Nemi (%)", "Işık (lux)"]].copy()
        df_out["TarihSaat"] = df_out["TarihSaat"].dt.strftime('%Y-%m-%d')

        result = df_out.rename(columns={
            "TarihSaat": "date",
            "Sıcaklık (°C)": "temperature",
            "Hava Nemi (%)": "humidity",
            "Toprak Nemi (%)": "moisture",
            "Işık (lux)": "light"
        })

        return jsonify(result.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": f"Error processing data: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

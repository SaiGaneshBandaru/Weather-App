from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = Flask(__name__, static_folder="static", template_folder="templates")

# Home page route
@app.route("/")
def index():
    return render_template("index.html")

# Weather API route with error handling and sunrise/sunset
@app.route("/weather")
def weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City not provided"}), 400

    try:
        # Call OpenWeather API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5)  # 5-second timeout
        data = res.json()

        if res.status_code != 200:
            return jsonify({"error": data.get("message", "City not found")}), res.status_code

        # Convert sunrise/sunset from UNIX timestamp to HH:MM format considering timezone
        timezone_offset = data.get("timezone", 0)
        sunrise = datetime.utcfromtimestamp(data.get("sys", {}).get("sunrise", 0) + timezone_offset).strftime('%H:%M')
        sunset = datetime.utcfromtimestamp(data.get("sys", {}).get("sunset", 0) + timezone_offset).strftime('%H:%M')

        # Prepare weather data
        weather_data = {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temp": data.get("main", {}).get("temp"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "description": data.get("weather")[0].get("description") if data.get("weather") else "",
            "icon": data.get("weather")[0].get("icon") if data.get("weather") else "",
            "sunrise": sunrise,
            "sunset": sunset
        }

        return jsonify(weather_data)

    except requests.exceptions.RequestException:
        return jsonify({"error": "Network error — please try again"}), 500


# 3-day forecast route
@app.route("/forecast")
def forecast():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City not provided"}), 400

    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5)
        data = res.json()

        if res.status_code != 200:
            return jsonify({"error": data.get("message", "City not found")}), res.status_code

        # Group data by day
        daily_forecast = {}
        for item in data.get("list", []):
            date_txt = item.get("dt_txt").split(" ")[0]
            temp = item.get("main", {}).get("temp")
            icon = item.get("weather")[0].get("icon") if item.get("weather") else ""
            if date_txt not in daily_forecast:
                daily_forecast[date_txt] = {"min": temp, "max": temp, "icon": icon}
            else:
                daily_forecast[date_txt]["min"] = min(daily_forecast[date_txt]["min"], temp)
                daily_forecast[date_txt]["max"] = max(daily_forecast[date_txt]["max"], temp)

        # Only take the next 3 days
        next_3_days = list(daily_forecast.items())[:3]
        forecast_data = [{"date": d[0], "min": d[1]["min"], "max": d[1]["max"], "icon": d[1]["icon"]} for d in next_3_days]

        return jsonify(forecast_data)

    except requests.exceptions.RequestException:
        return jsonify({"error": "Network error — please try again"}), 500


if __name__ == "__main__":
    app.run(debug=True)

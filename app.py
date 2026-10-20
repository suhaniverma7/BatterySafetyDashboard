import numpy as np
import pandas as pd
from scipy.stats import norm
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
import io
import base64
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "IA2.csv")

warning_threshold = 13.48
critical_threshold = 15


def get_probability(temp_to_cal):
    z_score = (temp_to_cal - battery_temp_mean) / battery_temp_std
    probability = 1 - norm.cdf(z_score)
    probability_percent = probability * 100
    return probability_percent


def get_BMS_decision(temp):
    if temp < 13.48:
        return "Continue"
    elif 13.48 < temp < 15:
        return "Slow down/monitor"
    else:
        return "Stop/precautionary action"


def make_graph(data):
    fig, (hist_ax, line_ax, risk_ax) = plt.subplots(1, 3, figsize=(18, 5))
    bin_edges = np.histogram_bin_edges(data["battery_temp_C"], bins=10)
    bin_width = bin_edges[1] - bin_edges[0]
    sns.histplot(data=data, x="battery_temp_C", bins=bin_edges, ax=hist_ax)
    temperature_range = np.linspace(battery_temp_min, battery_temp_max, 300)
    normal_frequency = (
        norm.pdf(temperature_range, loc=battery_temp_mean, scale=battery_temp_std)
        * len(data)
        * bin_width
    )
    hist_ax.plot(temperature_range, normal_frequency, label="Normal distribution")
    hist_ax.set_xlabel("Battery Temperature (°C)")
    hist_ax.set_ylabel("Frequency")
    hist_ax.set_title("Histogram of the 50 Battery Temperatures")
    hist_ax.legend()
    sns.lineplot(data=data, x="battery_temp_C", y="time_s", ax=line_ax)
    line_ax.set_xlabel("Battery Temperature (°C)")
    line_ax.set_ylabel("Time (s)")
    line_ax.set_title("Battery Temperature vs Time")
    risk_ax.plot(
        np.arange(1, len(data) + 1),
        data["battery_temp_C"],
        marker="o",
        label="Battery temperature",
    )
    risk_ax.axhline(warning_threshold, color="orange", linestyle="--", label="Warning (13.48°C)")
    risk_ax.axhline(critical_threshold, color="red", linestyle="--", label="Critical (15°C)")
    risk_ax.set_xlabel("Observation")
    risk_ax.set_ylabel("Battery Temperature (°C)")
    risk_ax.set_title("Battery Temperature Risk Thresholds")
    risk_ax.legend()
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def dashboard():
    global data, battery_temp_mean, battery_temp_variance
    global battery_temp_std, battery_temp_min, battery_temp_max

    try:
        data = pd.read_csv(DATA_FILE)
        battery_temp_mean = data["battery_temp_C"].mean()
        battery_temp_variance = data["battery_temp_C"].var()
        battery_temp_std = data["battery_temp_C"].std()
        battery_temp_min = data["battery_temp_C"].min()
        battery_temp_max = data["battery_temp_C"].max()

        graph = make_graph(data)
        result = None
        error = None
        entered_temp = ""

        if request.method == "POST":
            entered_temp = request.form.get("temperature", "").strip()
            try:
                temp = float(entered_temp)
                result = {
                    "temperature": temp,
                    "decision": get_BMS_decision(temp=temp),
                    "input_probability": get_probability(temp_to_cal=temp),
                    "warning_probability": get_probability(temp_to_cal=warning_threshold),
                    "critical_probability": get_probability(temp_to_cal=critical_threshold),
                }
            except ValueError:
                error = "Enter a valid temperature."

        preview = data.head(100).round(3)
        table_html = preview.to_html(index=False, classes="data-table", border=0)
        stats = {
            "rows": len(data),
            "mean": round(battery_temp_mean, 2),
            "std": round(battery_temp_std, 2),
            "min": round(battery_temp_min, 2),
            "max": round(battery_temp_max, 2),
        }

        return render_template(
            "index.html", stats=stats, graph=graph, table_html=table_html,
            result=result, error=error, entered_temp=entered_temp,
            warning=warning_threshold, critical=critical_threshold
        )
    except (FileNotFoundError, KeyError, pd.errors.ParserError, ZeroDivisionError) as exc:
        return render_template(
            "index.html", setup_error=f"Could not load IA2.csv: {exc}",
            stats=None, graph=None, table_html=None, result=None,
            error=None, entered_temp="", warning=warning_threshold,
            critical=critical_threshold
        )


if __name__ == "__main__":
    app.run(debug=True)

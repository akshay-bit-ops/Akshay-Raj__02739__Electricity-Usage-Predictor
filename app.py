import base64
import io
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, render_template_string, request

BILL_RATE = 6.0
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Electricity Usage Predictor</title>
  <style>
    :root { color-scheme: dark; --bg:#0b1220; --panel:#121e31; --line:#26364e; --muted:#9fb0c7; --cyan:#48d6e8; --green:#70e0ad; }
    * { box-sizing:border-box; } body { margin:0; font-family:Inter,system-ui,Arial,sans-serif; background:radial-gradient(circle at 80% 0%,#17304a 0,transparent 35%),var(--bg); color:#edf5ff; }
    .wrap { max-width:1050px; margin:auto; padding:42px 20px 70px; } .eyebrow { color:var(--cyan); letter-spacing:.16em; font-size:.75rem; font-weight:800; text-transform:uppercase; }
    h1 { font-size:clamp(2.2rem,6vw,4.5rem); line-height:1.02; margin:12px 0; } .lead { color:var(--muted); max-width:680px; line-height:1.7; }
    .grid { display:grid; grid-template-columns:1.1fr .9fr; gap:18px; margin-top:28px; } .panel { background:linear-gradient(145deg,#15243a,#101a2b); border:1px solid var(--line); border-radius:20px; padding:24px; box-shadow:0 18px 55px #0003; }
    h2 { margin:0 0 16px; font-size:1.15rem; } label { display:block; margin:16px 0 8px; color:#c9d8e9; font-weight:650; }
    input[type=file],input[type=number] { width:100%; border:1px solid #3a4d68; background:#0b1525; color:#edf5ff; border-radius:10px; padding:13px; }
    button { margin-top:18px; border:0; border-radius:10px; padding:13px 20px; background:var(--cyan); color:#07131d; font-weight:850; cursor:pointer; width:100%; font-size:1rem; }
    .hint,.muted { color:var(--muted); font-size:.9rem; line-height:1.6; } .error { margin-top:18px; padding:14px; border:1px solid #a94b58; background:#421e2a; border-radius:12px; color:#ffd9df; }
    .metrics { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; } .metric { background:#0b1525; border:1px solid var(--line); border-radius:14px; padding:16px; } .metric span { display:block; color:var(--muted); font-size:.82rem; } .metric strong { display:block; margin-top:8px; font-size:1.55rem; color:var(--green); overflow-wrap:anywhere; }
    .result { margin-top:18px; } .chart { width:100%; border-radius:12px; margin-top:18px; background:#fff; } table { border-collapse:collapse; width:100%; margin-top:16px; } th,td { padding:10px; border-bottom:1px solid var(--line); text-align:left; } th { color:var(--cyan); }
    .footer { margin-top:25px; color:var(--muted); font-size:.82rem; } code { color:var(--cyan); } @media(max-width:760px){.grid{grid-template-columns:1fr}.wrap{padding-top:28px}}
  </style>
</head>
<body><main class="wrap">
  <div class="eyebrow">PS No. 62 · Python + NumPy</div>
  <h1>Electricity<br>Usage Predictor<span style="color:var(--cyan)">.</span></h1>
  <p class="lead">Upload your monthly meter-usage CSV, fit a simple linear regression model, and estimate next-month consumption and bill. Built around the original project specification.</p>
  <div class="grid">
    <section class="panel">
      <h2>Run a prediction</h2>
      <form method="post" enctype="multipart/form-data">
        <label for="csv">Monthly usage CSV</label>
        <input id="csv" name="csv" type="file" accept=".csv,text/csv" required>
        <p class="hint">Required columns: Month, Units. Example: 1,120 on each row. At least two valid months are required.</p>
        <label for="month">Month to predict</label>
        <input id="month" name="month" type="number" min="0.01" step="any" value="{{ month or 5 }}" required>
        <button type="submit">Calculate prediction →</button>
      </form>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
    </section>
    <section class="panel">
      <h2>Model details</h2>
      <div class="metrics">
        <div class="metric"><span>Regression</span><strong style="font-size:1.1rem">Linear</strong></div>
        <div class="metric"><span>Bill rate</span><strong>₹6/unit</strong></div>
        <div class="metric"><span>Library</span><strong style="font-size:1.1rem">NumPy</strong></div>
        <div class="metric"><span>Input</span><strong style="font-size:1.1rem">CSV</strong></div>
      </div>
      <p class="hint" style="margin-top:18px">Model equation: <code>Units = slope × Month + intercept</code>. R² describes fit to the uploaded historical data; it does not guarantee future accuracy.</p>
    </section>
  </div>
  {% if result %}
  <section class="panel result">
    <div class="eyebrow">Prediction result</div><h2 style="margin-top:8px">Month {{ result.month }}</h2>
    <div class="metrics">
      <div class="metric"><span>Predicted usage</span><strong>{{ result.units }} units</strong></div>
      <div class="metric"><span>Estimated bill</span><strong>₹{{ result.bill }}</strong></div>
      <div class="metric"><span>Slope</span><strong>{{ result.slope }}</strong></div>
      <div class="metric"><span>Intercept</span><strong>{{ result.intercept }}</strong></div>
      <div class="metric"><span>R² score</span><strong>{{ result.r2 }}</strong></div>
      <div class="metric"><span>Data points</span><strong>{{ result.count }}</strong></div>
    </div>
    {% if result.units_raw < 0 %}<p class="error">The fitted line predicts negative usage. This is not physically meaningful; avoid relying on this extrapolation.</p>{% endif %}
    <h2 style="margin-top:24px">Actual usage vs regression line</h2>
    <img class="chart" src="data:image/png;base64,{{ result.chart }}" alt="Actual usage points and fitted regression line">
    <p class="muted">The estimate uses the fixed project rate of ₹6 per unit. Actual electricity bills may include additional charges and slab rates.</p>
    <table><thead><tr><th>Month</th><th>Actual units</th></tr></thead><tbody>{% for row in result.rows %}<tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td></tr>{% endfor %}</tbody></table>
  </section>
  {% endif %}
  <p class="footer">Educational project · Python 3 · Pandas · NumPy · Matplotlib · Flask</p>
</main></body></html>
"""

def read_usage_csv(file_storage):
    try:
        text = file_storage.read().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Please upload a UTF-8 encoded CSV file.") from exc
    if not text.strip():
        raise ValueError("The uploaded CSV is empty.")
    try:
        raw = pd.read_csv(io.StringIO(text), header=None, comment="#", skip_blank_lines=True)
    except pd.errors.ParserError as exc:
        raise ValueError("CSV format is invalid. Use two columns: Month, Units.") from exc
    if raw.empty or raw.shape[1] < 2:
        raise ValueError("CSV must contain two columns: Month and Units.")
    raw = raw.iloc[:, :2].copy()
    first = [str(v).strip().lower() for v in raw.iloc[0].tolist()]
    if first[0] in ("month", "months") or first[1] in ("units", "usage", "consumption"):
        raw = raw.iloc[1:].copy()
    raw.columns = ["Month", "Units"]
    raw["Month"] = pd.to_numeric(raw["Month"], errors="coerce")
    raw["Units"] = pd.to_numeric(raw["Units"], errors="coerce")
    if raw.empty:
        raise ValueError("CSV has a header but no usage records.")
    if raw[["Month", "Units"]].isna().any().any():
        raise ValueError("CSV contains missing or non-numeric Month/Units values. Correct the file and try again.")
    if (raw["Month"] <= 0).any():
        raise ValueError("Month values must be greater than zero.")
    if (raw["Units"] < 0).any():
        raise ValueError("Units cannot be negative.")
    if raw["Month"].duplicated().any():
        raise ValueError("Each month must appear only once in the CSV.")
    return raw.sort_values("Month").reset_index(drop=True)

def build_chart(data, slope, intercept, month, predicted):
    x = data["Month"].to_numpy(dtype=float)
    y = data["Units"].to_numpy(dtype=float)
    line_x = np.linspace(min(x.min(), month), max(x.max(), month), 120)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(x, y, color="#1677c8", s=65, label="Actual usage", zorder=3)
    ax.plot(line_x, slope * line_x + intercept, color="#e45757", linewidth=2.5, label="Regression line")
    ax.scatter([month], [predicted], color="#169b62", marker="X", s=100, label="Predicted month", zorder=4)
    ax.set(title="Actual vs Predicted Electricity Usage", xlabel="Month", ylabel="Units consumed")
    ax.grid(alpha=.25)
    ax.legend()
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    result = None
    month_value = request.form.get("month", "5") if request.method == "POST" else "5"
    if request.method == "POST":
        try:
            upload = request.files.get("csv")
            if upload is None or not upload.filename:
                raise ValueError("Choose a CSV file before submitting.")
            data = read_usage_csv(upload)
            if len(data) < 2:
                raise ValueError("At least 2 months of data are required for prediction.")
            try:
                month = float(month_value)
            except (TypeError, ValueError) as exc:
                raise ValueError("Enter a valid numeric month.") from exc
            if not np.isfinite(month) or month <= 0:
                raise ValueError("Month must be a positive number.")
            x = data["Month"].to_numpy(dtype=float)
            y = data["Units"].to_numpy(dtype=float)
            slope, intercept = np.polyfit(x, y, 1)
            fitted = slope * x + intercept
            ss_res = float(np.sum((y - fitted) ** 2))
            ss_tot = float(np.sum((y - np.mean(y)) ** 2))
            r2 = 1.0 if np.isclose(ss_tot, 0) and np.isclose(ss_res, 0) else (0.0 if np.isclose(ss_tot, 0) else 1 - ss_res / ss_tot)
            predicted = float(slope * month + intercept)
            result = {
                "month": f"{month:g}", "units": f"{predicted:.2f}",
                "units_raw": predicted, "bill": f"{predicted * BILL_RATE:.2f}",
                "slope": f"{slope:.2f}", "intercept": f"{intercept:.2f}",
                "r2": f"{r2:.2f}", "count": len(data),
                "chart": build_chart(data, slope, intercept, month, predicted),
                "rows": data.round(2).values.tolist()
            }
        except ValueError as exc:
            error = str(exc)
        except Exception:
            app.logger.exception("Prediction failed")
            error = "Something went wrong while processing the CSV. Check its format and try again."
    return render_template_string(PAGE, error=error, result=result, month=month_value)

@app.errorhandler(413)
def file_too_large(_error):
    return render_template_string(PAGE, error="File is too large. Maximum upload size is 2 MB.", result=None, month="5"), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

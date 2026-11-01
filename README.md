# ⚡ Electricity Usage Predictor

A Python project for **PS No. 62** that analyses historical monthly electricity consumption, fits a simple linear regression model, predicts usage for a selected future month, estimates the bill, and visualises the trend.

The original console-based workflow is retained in `electricity_predictor.py`. A Flask web interface is also included so the project can be used in a browser and deployed as a Python web service on Render.

## ✨ Features

- Load monthly usage records from a CSV file using Pandas.
- Validate missing, non-numeric, negative, and duplicate values.
- Fit a degree-1 regression line with NumPy `polyfit()`.
- Calculate slope, intercept, and coefficient of determination (R²).
- Predict electricity usage for a user-selected month.
- Estimate the bill at the assignment rate of **₹6 per unit**.
- Plot actual usage, the regression line, and the predicted point with Matplotlib.
- Handle the minimum-data case: at least two valid months are required.
- Use the original console application or the browser-based Flask interface.

## 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Application logic |
| Pandas | CSV loading and data validation |
| NumPy | Linear regression and R² calculation |
| Matplotlib | Actual vs predicted chart |
| Flask | Browser-based interface |
| Gunicorn | Production WSGI server on Render |

## 📁 Project Structure

```text
Electricity-Usage-Predictor/
├── app.py                    # Flask web application (Render entry point)
├── electricity_predictor.py  # Original command-line application
├── usage.csv                 # Sample monthly usage data
├── Demo.csv                  # Assignment test-case examples
├── Output.csv                # Expected test-case outputs
├── requirements.txt          # Python dependencies
├── render.yaml               # Render deployment configuration
├── .gitignore
└── README.md
```

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Ayushkumarxy/Akshay-Raj__02739__Electricity-Usage-Predictor.git
cd Akshay-Raj__02739__Electricity-Usage-Predictor
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the web application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser, upload a CSV file, enter the month to predict, and submit.

### Run the original console version

```bash
python electricity_predictor.py
```

The console program reads `usage.csv` from the project directory.

## 📄 CSV Format

Both header and headerless CSV files are supported.

```csv
Month,Units
1,200
2,220
3,240
4,260
```

Or:

```csv
1,200
2,220
3,240
4,260
```

Rules:
- The CSV must contain at least two columns: Month and Units.
- Month values must be positive and unique.
- Units must be numeric and cannot be negative.
- At least two valid data rows are required.

## 🧮 How the Model Works

The application fits a straight line:

```text
Units = slope × Month + intercept
```

NumPy's `polyfit(month, units, 1)` calculates the slope and intercept. The fitted values are then used to calculate R²:

```text
R² = 1 - (sum of squared residuals / total sum of squares)
```

The bill estimate is:

```text
Estimated Bill = Predicted Units × ₹6
```

R² measures how closely the fitted line matches the uploaded historical data. It is not a guarantee of future prediction accuracy. Predictions far beyond the observed months are extrapolations and should be interpreted cautiously. The ₹6 rate is the fixed assignment assumption, not a complete real-world tariff.

## 🧪 Assignment Test Cases

The project brief specifies these expected outcomes:

| Test case | Input | Expected result |
|---|---|---|
| Normal input | (1,120), (2,220), (3,240), (4,260) | Slope 20, intercept 180, Month 5 = 280 units, bill ₹1,680 |
| Minimum input | (1,100), (2,150) | Slope 50, intercept 50, Month 3 = 200 units, bill ₹1,200 |
| Invalid input | One data row only | Error: at least 2 months are required |
| Different valid data | (1,100), (2,120), (3,150), (4,170) | Slope 24, intercept 75, R² ≈ 0.99, Month 6 = 219 units, bill ₹1,314 |

> Note: the first case above follows the assignment's expected output values. The repository's `usage.csv` is a separate sample dataset.

## ☁️ Deploy on Render

This repository includes a `render.yaml` Blueprint configuration.

1. Sign in to Render and choose **New → Blueprint** (or create a **Web Service**).
2. Connect the GitHub repository: `Ayushkumarxy/Akshay-Raj__02739__Electricity-Usage-Predictor`.
3. If creating a Web Service manually, select:
   - **Runtime:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Deploy and wait for the build to finish.
5. Open the generated `.onrender.com` URL and test it with a CSV upload.

No environment variables or external database are required. The app listens on Render's assigned `PORT`.

## ⚠️ Limitations

- This is a learning project using simple linear regression and a small history of monthly data.
- Real electricity tariffs may include fixed charges, taxes, and slab-based pricing; the app uses the assignment's flat ₹6/unit rate.
- A high R² on a small dataset does not guarantee accurate future forecasts.
- Uploaded CSV data is processed for the request and is not saved as a user account or permanent dataset.

## 👨‍💻 Repository

[View source code on GitHub](https://github.com/Ayushkumarxy/Akshay-Raj__02739__Electricity-Usage-Predictor)

---

**Project No.:** 62 · **Project Title:** Electricity Usage Predictor

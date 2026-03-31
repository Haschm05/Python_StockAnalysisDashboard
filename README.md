# Stock Analysis Dashboard

A Python-based desktop application that provides an interactive GUI for stock data analysis using data from Yahoo Finance. This tool allows users to visualize stock trends, compute statistics, and generate forecasts—all within a scrollable dashboard interface.

---

## Features

### Data Analysis

* Fetch historical stock data using Yahoo Finance
* Visualize:
  * Closing price trends
  * Moving averages
  * Trading volume
* Linear regression-based price forecasting
* Summary statistics:

  * Average price
  * Volatility (standard deviation)
  * Min/Max values

### GUI Interface

* Built with **Tkinter**
* Scrollable dashboard layout
* Embedded Matplotlib charts
* Interactive buttons for:

  * Fetching data
  * Generating dashboard
  * Saving results
  * Loading saved datasets

### Data Management

* Save dashboard outputs:
  * CSV data
  * Graph images (PNG)
  * Notes (TXT)
* Automatic archiving system for saved files
* Load previously saved datasets

---

## Tech Stack

* **Python**
* **Tkinter** – GUI framework
* **yfinance** – Stock data API
* **pandas / numpy** – Data processing
* **matplotlib** – Data visualization
* **os / shutil** – File handling

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/stock-analysis-dashboard.git
cd stock-analysis-dashboard
```

2. Install dependencies:

```bash
pip install yfinance pandas numpy matplotlib
```

3. Run the application:

```bash
python main.py
```

---

## Usage

1. Enter a stock ticker (e.g., `AAPL`, `TSLA`)
2. Set:

   * Time period (e.g., `6mo`, `1y`)
   * Moving average window
3. Click **"Fetch Data"**
4. Click **"Generate Dashboard"**

Optional:

* Save results using **"Save Dashboard"**
* Load previous data using **"Load Saved Data"**

---

## Project Structure

```
Application/
│── SavedData/     # Temporary storage before archiving
│── Archive/       # Stored results (CSV, PNG, TXT)

main.py            # Main application file
```

---

## Dashboard Includes

* Price + Moving Average chart
* Volume bar chart
* Linear regression forecast (30-day projection)
* Summary statistics panel

---

## Notes

* Requires an internet connection to fetch stock data
* Data is sourced from Yahoo Finance via `yfinance`
* Forecasting uses a simple linear regression model (not financial advice)

---

## Future Improvements

* Multi-stock tracking & watchlists
* Machine learning-based predictions
* Automated trading integration
* Refactor into modular classes
* Improved UI/UX design
* Convert into standalone desktop application

---

## Author

**Hayden Schmidt**
Last Updated: Dec 4, 2025

---

## License

This project is open-source and available under the MIT License.

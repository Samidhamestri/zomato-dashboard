# Zomato Restaurant Analysis Dashboard

An interactive data analysis dashboard built with Streamlit and Plotly, exploring restaurant trends across Bengaluru using the Zomato dataset.

**[🔗 Live Dashboard →](your-streamlit-url-here)**

---

## What this shows

- **Top cuisines by average rating** — which food categories score highest
- **Cost vs Rating scatter** — does higher price mean better food?
- **Online ordering trends** — how restaurants are adapting to delivery culture
- **Key business insights** — auto-generated from filtered data

## Key findings

- Budget restaurants (≤₹300 for 2) hold their own against premium options on ratings
- Only ~X% of restaurants achieve a 4.0+ rating, making high-rated venues a strong discovery filter
- Online ordering has crossed majority adoption in most Bengaluru areas

## Tech stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| Streamlit | Dashboard framework |
| Pandas | Data cleaning & analysis |
| Plotly Express | Interactive charts |

## Run locally

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/zomato-dashboard.git
cd zomato-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add the dataset
# Download zomato.csv from Kaggle (link below) and place in this folder

# 4. Run
streamlit run app.py
```

## Dataset

[Zomato Bangalore Restaurants — Kaggle](https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants)

Download `zomato.csv` and place it in the root of this project folder.

## Data cleaning steps

1. **Ratings** — extracted numeric value from "4.1/5" string format; dropped null/NEW entries
2. **Cost** — removed commas from "1,200" format; converted to integer
3. **Primary cuisine** — extracted first listed cuisine from comma-separated field
4. **Filtering** — removed restaurants with no rating data

---

*Built by Samidha Mestri · MBA Tech (AI & ML), RAIT Navi Mumbai*

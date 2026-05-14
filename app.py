# ============================================================
# ZOMATO RESTAURANT ANALYSIS DASHBOARD
# Built with Streamlit + Plotly
# ============================================================
# HOW STREAMLIT WORKS:
# Streamlit reruns this entire file top-to-bottom every time
# the user interacts with a filter or button. That's it.
# No callbacks, no event listeners — just Python that reruns.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ── PAGE CONFIGURATION ───────────────────────────────────────
# This must be the FIRST Streamlit command in your file.
# layout="wide" uses the full browser width instead of a narrow column.
st.set_page_config(
    page_title="Zomato Restaurant Analysis",
    page_icon="🍽️",
    layout="wide"
)

# ── CUSTOM CSS ───────────────────────────────────────────────
# We inject a small style block to tighten up the default Streamlit spacing.
# st.markdown() renders raw HTML/CSS. unsafe_allow_html=True is required for this.
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-card {
        background-color: #f8f8f8;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)


# ── LOAD & CLEAN DATA ────────────────────────────────────────
# @st.cache_data tells Streamlit: run this function ONCE, then
# store the result in memory. Without this, your data would
# reload from disk on every single user interaction — very slow.
@st.cache_data
def load_data():
    df = pd.read_csv("zomato_sample.csv")

    # ── CLEANING STEP 1: Ratings ─────────────────────────────
    # The 'rate' column looks like "4.1/5" or "NEW" or "-"
    # We need a plain number. Steps:
    #   1. Convert everything to string (in case of floats)
    #   2. Keep only the part before the "/" character
    #   3. Strip whitespace
    #   4. Replace non-numeric strings with NaN
    #   5. Convert to float
    df['rate'] = (
        df['rate']
        .astype(str)
        .str.split('/').str[0]
        .str.strip()
        .replace({'NEW': None, '-': None, 'nan': None})
    )
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

    # ── CLEANING STEP 2: Cost ────────────────────────────────
    # 'approx_cost(for two people)' has commas: "1,200" → 1200
    # We rename it to 'cost' for convenience.
    df = df.rename(columns={'approx_cost(for two people)': 'cost'})
    df['cost'] = (
        df['cost']
        .astype(str)
        .str.replace(',', '', regex=False)
    )
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce')

    # ── CLEANING STEP 3: Column names ────────────────────────
    # 'listed_in(city)' has special characters — rename it.
    df = df.rename(columns={'listed_in(city)': 'city', 'listed_in(type)': 'meal_type'})

    # ── CLEANING STEP 4: Drop rows with no rating ────────────
    # A dashboard about ratings is useless with empty rating rows.
    df = df.dropna(subset=['rate'])

    # ── CLEANING STEP 5: Cuisines ────────────────────────────
    # Each row has multiple cuisines: "North Indian, Chinese, Mughlai"
    # We take only the FIRST cuisine listed as the primary one.
    df['primary_cuisine'] = df['cuisines'].astype(str).str.split(',').str[0].str.strip()

    return df


# Load the data (cached after first run)
df = load_data()


# ── SIDEBAR FILTERS ──────────────────────────────────────────
# st.sidebar.anything() puts that element in the left sidebar.
# Everything here creates a "filtered_df" that the charts below will use.

st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Use these to explore the data.")

# Filter 1: City
# sorted() keeps the dropdown alphabetical.
# default = all cities selected (no filter applied at start)
all_cities = sorted(df['city'].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect(
    label="City / Area",
    options=all_cities,
    default=all_cities[:5]   # start with first 5 to avoid overloading
)

# Filter 2: Rating range
# st.slider() with two values creates a RANGE slider (min, max)
min_rating, max_rating = st.sidebar.slider(
    label="Rating range",
    min_value=float(df['rate'].min()),
    max_value=float(df['rate'].max()),
    value=(3.0, 5.0),          # default: 3.0 to 5.0
    step=0.1
)

# Filter 3: Online order
online_options = ["All", "Yes", "No"]
selected_online = st.sidebar.radio(
    label="Accepts online orders?",
    options=online_options,
    index=0    # default = "All"
)

# ── APPLY FILTERS ─────────────────────────────────────────────
# We build filtered_df by chaining conditions using & (AND).
# Each condition creates a boolean Series; & combines them.

filtered_df = df[
    (df['city'].isin(selected_cities)) &
    (df['rate'] >= min_rating) &
    (df['rate'] <= max_rating)
]

# Apply the online order filter only if it's not "All"
if selected_online != "All":
    filtered_df = filtered_df[filtered_df['online_order'] == selected_online]


# ── DASHBOARD HEADER ──────────────────────────────────────────
st.title("🍽️ Zomato Restaurant Analysis")
st.markdown("Explore restaurant ratings, costs, and trends across Bengaluru.")
st.markdown("---")   # horizontal divider


# ── METRIC CARDS ─────────────────────────────────────────────
# st.columns(4) creates 4 equal-width columns side by side.
# We unpack them into variables: col1, col2, col3, col4.
# Then use "with col1:" to place content inside that column.

col1, col2, col3, col4 = st.columns(4)

with col1:
    # len() counts rows = number of restaurants matching filters
    st.metric(label="🏪 Restaurants found", value=f"{len(filtered_df):,}")

with col2:
    # .mean() averages the rating column; :.2f rounds to 2 decimals
    avg_rating = filtered_df['rate'].mean()
    st.metric(label="⭐ Avg rating", value=f"{avg_rating:.2f}")

with col3:
    avg_cost = filtered_df['cost'].mean()
    st.metric(label="💰 Avg cost for 2", value=f"₹{avg_cost:,.0f}")

with col4:
    # value_counts() counts occurrences; .idxmax() returns the top label
    top_cuisine = filtered_df['primary_cuisine'].value_counts().idxmax()
    st.metric(label="🥘 Top cuisine", value=top_cuisine)

st.markdown("---")


# ── CHARTS ───────────────────────────────────────────────────
# We use Plotly Express (px) for charts — it creates interactive
# charts with hover tooltips, zoom, and download built in.
# st.plotly_chart() renders them inside Streamlit.
# use_container_width=True makes the chart fill its column width.

chart_col1, chart_col2 = st.columns(2)

# ── CHART 1: Top 10 Cuisines by Average Rating ───────────────
with chart_col1:
    st.subheader("Top 10 Cuisines by Avg Rating")
    st.caption("Which cuisines score highest? Min 10 restaurants to qualify.")

    # groupby('primary_cuisine') groups rows by cuisine
    # agg() calculates multiple things at once: mean rating + count
    # reset_index() turns the grouped result back into a normal dataframe
    cuisine_stats = (
        filtered_df
        .groupby('primary_cuisine')
        .agg(avg_rating=('rate', 'mean'), count=('rate', 'count'))
        .reset_index()
    )

    # Only show cuisines with at least 10 restaurants (avoids misleading averages)
    cuisine_stats = cuisine_stats[cuisine_stats['count'] >= 10]

    # Sort by avg_rating descending, take top 10
    cuisine_stats = cuisine_stats.sort_values('avg_rating', ascending=False).head(10)

    # px.bar() creates a bar chart
    # x = column for x-axis, y = column for y-axis
    # color = column that determines bar color gradient
    # hover_data = extra columns shown in tooltip on hover
    fig1 = px.bar(
        cuisine_stats,
        x='avg_rating',
        y='primary_cuisine',
        orientation='h',           # horizontal bar chart
        color='avg_rating',
        color_continuous_scale='RdYlGn',   # Red→Yellow→Green gradient
        hover_data=['count'],
        labels={'avg_rating': 'Avg Rating', 'primary_cuisine': 'Cuisine', 'count': 'No. of restaurants'},
        text='avg_rating'          # show value on each bar
    )
    fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig1.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=380
    )
    st.plotly_chart(fig1, use_container_width=True)


# ── CHART 2: Cost vs Rating Scatter ──────────────────────────
with chart_col2:
    st.subheader("Cost vs Rating")
    st.caption("Does spending more mean better food?")

    # Sample up to 1000 points to avoid a cluttered chart
    # random_state=42 makes the sample reproducible (same points each run)
    sample_df = filtered_df.dropna(subset=['cost']).sample(
        n=min(1000, len(filtered_df.dropna(subset=['cost']))),
        random_state=42
    )

    # px.scatter() creates a scatter plot
    # Each dot = one restaurant
    # color='online_order' colors dots by whether they accept online orders
    fig2 = px.scatter(
        sample_df,
        x='cost',
        y='rate',
        color='online_order',
        hover_data=['name', 'primary_cuisine'],
        labels={'cost': 'Cost for 2 (₹)', 'rate': 'Rating', 'online_order': 'Online Order'},
        opacity=0.5,           # semi-transparent dots (avoids overplotting)
        color_discrete_map={'Yes': '#E23744', 'No': '#999999'}
    )
    fig2.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig2, use_container_width=True)


# ── CHART 3: Online Orders vs Table Booking Breakdown ────────
st.subheader("Restaurant Type Breakdown")
st.caption("What share of restaurants offer online ordering vs table booking?")

pie_col1, pie_col2, pie_spacer = st.columns([1, 1, 1])

with pie_col1:
    # value_counts() counts Yes/No in online_order column
    # reset_index() makes it a dataframe with columns 'online_order' and 'count'
    online_counts = filtered_df['online_order'].value_counts().reset_index()
    online_counts.columns = ['online_order', 'count']

    fig3 = px.pie(
        online_counts,
        names='online_order',
        values='count',
        title='Accepts Online Orders',
        color_discrete_map={'Yes': '#E23744', 'No': '#cccccc'},
        hole=0.4    # donut chart — looks cleaner than solid pie
    )
    fig3.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300)
    st.plotly_chart(fig3, use_container_width=True)

with pie_col2:
    booking_counts = filtered_df['book_table'].value_counts().reset_index()
    booking_counts.columns = ['book_table', 'count']

    fig4 = px.pie(
        booking_counts,
        names='book_table',
        values='count',
        title='Accepts Table Booking',
        color_discrete_map={'Yes': '#E23744', 'No': '#cccccc'},
        hole=0.4
    )
    fig4.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300)
    st.plotly_chart(fig4, use_container_width=True)


# ── INSIGHT PANEL ─────────────────────────────────────────────
# This is the section that turns a "student project" into something
# that looks like real analysis. Don't skip this.
st.markdown("---")
st.subheader("📌 Key Insights")

# We compute real numbers to populate the insight text dynamically
online_pct = (filtered_df['online_order'] == 'Yes').mean() * 100
high_rated = filtered_df[filtered_df['rate'] >= 4.0]
high_rated_pct = len(high_rated) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
budget_avg = filtered_df[filtered_df['cost'] <= 300]['rate'].mean()
premium_avg = filtered_df[filtered_df['cost'] > 800]['rate'].mean()

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.info(f"""
    **Online ordering is mainstream**
    {online_pct:.0f}% of restaurants in the selected areas accept online orders.
    Restaurants without online ordering risk losing visibility on platforms.
    """)

with insight_col2:
    st.success(f"""
    **Quality is achievable on a budget**
    Budget restaurants (≤₹300 for 2) average a **{budget_avg:.2f}** rating —
    compared to **{premium_avg:.2f}** for premium (>₹800).
    Price alone doesn't predict a good experience.
    """)

with insight_col3:
    st.warning(f"""
    **High ratings are rare**
    Only **{high_rated_pct:.1f}%** of restaurants score 4.0 or above.
    This makes top-rated restaurants a strong filter for food discovery features.
    """)


# ── RAW DATA TABLE (optional toggle) ──────────────────────────
# st.expander() creates a collapsible section — good for raw data
# that most users don't need but technical viewers appreciate.
with st.expander("🔎 View raw data"):
    st.dataframe(
        filtered_df[['name', 'city', 'primary_cuisine', 'rate', 'cost', 'online_order', 'book_table']]
        .sort_values('rate', ascending=False)
        .reset_index(drop=True),
        use_container_width=True
    )
    st.caption(f"Showing {len(filtered_df):,} restaurants matching current filters.")


# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data source: Zomato Bengaluru dataset via Kaggle · Built with Streamlit + Plotly")

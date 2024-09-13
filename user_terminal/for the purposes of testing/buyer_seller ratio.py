import altair as alt
import pandas as pd
import sqlite3
import streamlit as st

try:
    buy_volume = curs_exchange.execute(
        "SELECT SUM(quantity) FROM active_orders WHERE buy_or_sell='buy'"
    ).fetchone()[0] or 0

    sell_volume = curs_exchange.execute(
        "SELECT SUM(quantity) FROM active_orders WHERE buy_or_sell='sell'"
    ).fetchone()[0] or 0

    total_volume = buy_volume + sell_volume
    buy_percentage = (buy_volume / total_volume) * 100 if total_volume != 0 else 0
    sell_percentage = (sell_volume / total_volume) * 100 if total_volume != 0 else 0

    ratio_data = pd.DataFrame({
        'Type': ['Buy Volume', 'Sell Volume'],
        'Percentage': [buy_percentage, sell_percentage]
    })

    # Create a base chart for buyers
    buy_bar = alt.Chart(ratio_data[ratio_data['Type'] == 'Buy Volume']).mark_bar().encode(
        x=alt.X('Percentage:Q', axis=None, scale=alt.Scale(domain=[0, 100])),
        y=alt.value(1),
        color=alt.value('#32CD32')
    ).properties(
        height=50,
        width=500
    )

    # Create a base chart for sellers
    sell_bar = alt.Chart(ratio_data[ratio_data['Type'] == 'Sell Volume']).mark_bar().encode(
        x=alt.X('Percentage:Q', axis=None, scale=alt.Scale(domain=[0, 100])),
        y=alt.value(1),
        color=alt.value('#FF6347')
    ).properties(
        height=50,
        width=500
    )

    # Position the sell bar to the right
    sell_bar = sell_bar.transform_calculate(
        Percentage='-datum.Percentage'
    ).encode(
        x=alt.X('Percentage:Q', axis=None, scale=alt.Scale(domain=[-100, 0]))
    )

    # Combine the charts
    combined_chart = alt.layer(buy_bar, sell_bar).resolve_scale(x='shared')

    # Add text to the bars
    buy_text = buy_bar.mark_text(
        align='left',
        baseline='middle',
        dx=5
    ).encode(
        text=alt.Text('Percentage:Q', format='.1f')
    )

    sell_text = sell_bar.mark_text(
        align='right',
        baseline='middle',
        dx=-5
    ).encode(
        text=alt.Text('Percentage:Q', format='.1f')
    )

    st.altair_chart(combined_chart + buy_text + sell_text, use_container_width=True)

    st.write(f"Buyers to Sellers Ratio: {buy_volume / sell_volume if sell_volume != 0 else float('inf'):.2f}")
except sqlite3.Error as e:
    st.error(f"An error occurred: {e}")

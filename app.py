#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# importing important libraries
import pandas as pd
import numpy as np
import seaborn as sns                       #visualisation
import matplotlib.pyplot as plt             #visualisation
import plotly.express as px                 # for interactive visualization



# read the dataset and display attributes
df=pd.read_csv(r"https://raw.githubusercontent.com/Heritier1990/supermarket-sales-dashboard/refs/heads/main/SampleSuperstore.csv")


               
# Create Treemap with fixed color scale
fig1 = px.treemap(
    df,
    path=["Sub_Category"],  # Only Sub-Category in the hierarchy
    values="Sales",         # Size of blocks based on Sales
    color="Profit",         # Color based on Profit
    color_continuous_scale="Blues",  # Red (loss) → Yellow (neutral) → Green (profit)
    range_color=[-1000, 3000],  # FIXED color scale from -100 to 3000
    title="Treemap of Sales and Profit by Sub-Category"
)

# Show plot
fig1.show()



# Group data by Sub_Category and Segment, summing up the profit
df_grouped = df.groupby(['Sub_Category', 'Segment'])['Profit'].sum().reset_index()

# Sort Sub_Categories by total profit
df_sorted = df_grouped.groupby('Sub_Category')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False)

# Merge sorted order back
df_grouped['Sub_Category'] = pd.Categorical(df_grouped['Sub_Category'], categories=df_sorted['Sub_Category'], ordered=True)


# Create the bar chart
fig2 = px.bar(df_grouped, 
             x='Sub_Category', 
             y='Profit', 
             color='Segment', 
             title="Sorted Profit by Sub-Category and Customer Segment",
             barmode='stack',
             category_orders={"Sub_Category": df_sorted['Sub_Category'].tolist()},
             color_discrete_sequence=px.colors.qualitative.Set2)

fig2.update_layout(
    xaxis_title="Sub-Category", 
    yaxis_title="Total Profit", 
    xaxis={'categoryorder':'total descending'}, 
    bargap=0.1,
    template="plotly_white"
)

# Identify last 3 sub-categories with negative profit
negative_profits = df_sorted[df_sorted['Profit'] < 0]
last_three_neg = negative_profits.tail(3)['Sub_Category'].tolist()
# Add annotation on the positive side
if last_three_neg:
    # Place it above zero (e.g., 5000 units)
    fig2.add_annotation(
        x=last_three_neg[-3],  # X-axis location (first of the 3)
        y=5000,                 # Y-axis (above bars)
        text="⚠️ Supplies, Bookcases and Tables are yielding negative returns.",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50,  # Arrow goes downward
        font=dict(size=12),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="gray",
        borderwidth=1
    )

fig2.show()


# Create Scatter Plot
fig3 = px.scatter(
    df,
    x="Discount",       # X-axis: Discount percentage
    y="Profit",         # Y-axis: Profit
    color="Sub_Category",  # Color by Sub-Category for better comparison
    size="Sales",       # Bubble size represents Sales volume
    hover_data=["Region", "Sub_Category", "Sales"],  # Show extra details on hover
    title="Impact of Discount on Profit (Filter by Region)"
)

# Add interactive filter for Region
fig3.update_layout(
    updatemenus=[{
        "buttons": [
            {"label": "All Regions", "method": "update", "args": [{"visible": True}]}
        ] + [
            {"label": region, "method": "update",
             "args": [{"visible": df["Region"] == region}]}  # Filter by selected region
            for region in df["Region"].unique()
        ],
        "direction": "down",
        "showactive": True,
    }]
)

# Show interactive plot
fig3.show()


# Rename the categories
df['Discount_%'] = df['Discount_%'].replace({
    '0%': '0%',
    '0.1- 0.4%': ']0, 40%]',
    '0.5-0.8%': '>40%'
})


# Create Box Plot
fig4 = px.box(
    df,
    x="Discount_%",       # X-axis: Discount Ranges
    y="Profit",           # Y-axis: Profit
    color="Region",       # Color by Region for comparison
    title="Profit Distribution Across Different Discount Ranges",
    points="all",         # Show all points as dots
    hover_data=["Sub_Category", "Sales"]  # Show extra details on hover
)

# Show plot
fig4.show()


import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

fig2.layout.annotations = []  # Clear previous annotations

max_profit = df_grouped['Profit'].max()

fig2.add_annotation(
    x=last_three_neg[-3],
    y=0,
    text="⚠️ <b>Negative Returns</b><br>• Supplies<br>• Bookcases<br>• Tables",
    showarrow=True,
    arrowhead=2,
    ax=0,
    ay=-70,
    font=dict(size=11),
    align="left",
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="gray",
    borderwidth=1,
    borderpad=1
)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Supermarket Sales Analysis", className="text-center mb-4"),
    
    # Row 1: Treemap & Bar Chart
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig1), width=6),  # Treemap (Left)
        dbc.Col(dcc.Graph(figure=fig2), width=6)   # Bar Chart (Right)
    ], className="mb-4"),
    
    # Row 2: Scatter Plot & Box Plot
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig3), width=6),  # Scatter Plot (Left)
        dbc.Col(dcc.Graph(figure=fig4), width=6)   # Box Plot (Right)
    ])
])

# Run the app
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=port)


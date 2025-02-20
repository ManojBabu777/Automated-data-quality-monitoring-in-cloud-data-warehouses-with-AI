import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)

    # Convert order_date to datetime
    df["order_date"] = pd.to_datetime(df["order_date"], format="%d-%m-%Y", errors='coerce')

    # Count missing values before cleaning
    print("Missing values before cleaning:\n", df.isna().sum())

    # Handle missing values
    df.dropna(subset=["customer_id", "payment_method"], inplace=True)
    df.fillna({"order_amount": df["order_amount"].median()}, inplace=True)

    # Remove duplicates
    duplicates_removed = df.duplicated().sum()
    df.drop_duplicates(inplace=True)
    print(f"Removed {duplicates_removed} duplicate rows.")

    # Anomaly detection using Z-score (lowered threshold for better detection)
    if "order_amount" in df.columns:
        z_scores = np.abs((df["order_amount"] - df["order_amount"].mean()) / df["order_amount"].std())
        df["anomaly"] = z_scores > 1.5  # Lower threshold to detect more anomalies
        anomalies_detected = df["anomaly"].sum()
        print(f"Detected {anomalies_detected} anomalies.")
    else:
        df["anomaly"] = False

    return df

def create_plot(df, title, detect_anomalies=False):
    fig = go.Figure()
    
    # Histogram of Order Amount with better visualization
    if "order_amount" in df.columns:
        fig.add_trace(go.Histogram(x=df["order_amount"], name="Order Amount", opacity=0.7, marker_color='blue', nbinsx=50))
    
        # If detecting anomalies, mark them in a different color
        if detect_anomalies and "anomaly" in df.columns:
            anomalies = df[df["anomaly"]]
            fig.add_trace(go.Scatter(x=anomalies["order_amount"], y=[0]*len(anomalies), mode='markers', 
                                     marker=dict(color='red', size=8), name="Anomalies"))
    
    fig.update_layout(
        title=f"Order Amount Distribution - {title}",
        xaxis_title="Order Amount",
        yaxis_title="Count",
        barmode="overlay",
        height=600,
        width=1000
    )
    
    return fig

# Load data
file_path = "orders_data_set_final.csv"
df_raw = pd.read_csv(file_path)
df_cleaned = load_and_clean_data(file_path)

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Automated Data Quality Monitoring Dashboard"),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Before Cleaning', children=[
            dcc.Graph(figure=create_plot(df_raw, "Before Cleaning", detect_anomalies=False))
        ]),
        dcc.Tab(label='After Cleaning', children=[
            dcc.Graph(figure=create_plot(df_cleaned, "After Cleaning", detect_anomalies=True))
        ]),
        dcc.Tab(label='Anomalies', children=[
            dash_table.DataTable(
                id='anomalies-table',
                columns=[{"name": col, "id": col} for col in df_cleaned.columns],
                data=df_cleaned[df_cleaned["anomaly"]].to_dict(orient='records') if "anomaly" in df_cleaned.columns else [],
                page_size=10,
                style_table={'height': '400px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'}
            )
        ])
    ])
])

if __name__ == "__main__":
    app.run_server(debug=True)

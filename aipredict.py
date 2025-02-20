import streamlit as st
import requests
import json

# IBM Cloud API Credentials
API_KEY = "oVOaYR_8VB7r56f5wlQUENJ4HW_Y9U9kjR1e2X4IFu2p"  # Replace with your actual API key
DEPLOYMENT_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/b5ef2044-9f2a-47f3-b45c-ffda62b4312d/predictions?version=2021-05-01"

# Function to Get IBM Auth Token
def get_ibm_token():
    token_url = "https://iam.cloud.ibm.com/identity/token"
    payload = {"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}
    
    try:
        response = requests.post(token_url, data=payload, timeout=15)
        response.raise_for_status()
        return response.json().get("access_token")
    
    except requests.exceptions.Timeout:
        return "TIMEOUT_ERROR"
    except requests.exceptions.RequestException as e:
        return f"REQUEST_ERROR: {e}"

# Function to Predict Data Quality Issues
def predict_data_quality(user_inputs):
    token = get_ibm_token()
    if "ERROR" in token:
        return f" Authentication Failed: {token}"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "input_data": [
            {
                "fields": [
                    "order_id",
                    "customer_id",
                    "currency",
                    "order_date",
                    "status",
                    "country_code",
                    "payment_method",
                    "fraud_flag",
                    "delivery_days",
                    "customer_age",
                    "product_category"
                ],
                "values": [user_inputs]
            }
        ]
    }

    try:
        response = requests.post(DEPLOYMENT_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Extracting prediction result
        prediction = result["predictions"][0]["values"][0][0]
        return f" **Predicted Data Quality Issue:** {prediction}"

    except requests.exceptions.Timeout:
        return " IBM Cloud API Timeout. Please try again later."
    except requests.exceptions.RequestException as e:
        return f" API Request Error: {e}"

# Streamlit UI
def predict_page():
    st.title(" AI-Based Data Quality Monitoring")

    with st.form("data_quality_form"):
        order_id = st.number_input(" Order ID", min_value=10000, step=1)
        customer_id = st.number_input(" Customer ID", min_value=1000, step=1)
        currency = st.selectbox("Currency", ["USD", "INR", "EUR", "BTC"])
        order_date = st.date_input(" Order Date")
        status = st.selectbox(" Order Status", ["Completed", "Pending", "Cancelled"])
        country_code = st.text_input(" Country Code")
        payment_method = st.selectbox(" Payment Method", ["Credit Card", "Debit Card", "PayPal", "Bitcoin"])
        fraud_flag = st.selectbox(" Fraud Flag", ["Yes", "No"])
        delivery_days = st.number_input("Delivery Days", min_value=1, step=1)
        customer_age = st.number_input(" Customer Age", min_value=18, max_value=100, step=1)
        product_category = st.selectbox(" Product Category", ["Electronics", "Clothing", "Automotive", "Toys"])

        submit_button = st.form_submit_button("🔍 Check Data Quality")

    if submit_button:
        user_inputs = [
            order_id, customer_id, currency, str(order_date), status, country_code,
            payment_method, fraud_flag, delivery_days, customer_age, product_category
        ]
        
        result = predict_data_quality(user_inputs)
        st.success(result)

if __name__ == "__main__":
    predict_page()

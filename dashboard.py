
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
from babel.numbers import format_currency
from datetime import timedelta
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return daily_orders_df
def create_sum_order_items(df):
    sum_order_items_df = df.groupby("product_category_name").order_id.nunique().sort_values(
        ascending=False).reset_index()
    return sum_order_items_df

def create_bystate(df):
    cust_bystate_df = df.groupby(by='customer_state').customer_unique_id.nunique().reset_index()
    cust_bystate_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)
    return cust_bystate_df
def create_rfm_df(df):
    last = df['order_purchase_timestamp'].max()
    timebound = last + timedelta(days=1)

    df_rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (timebound - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'})
    df_rfm.reset_index(inplace=True)
    df_rfm.rename(columns={'order_purchase_timestamp': 'Recency',
                           'order_id': 'Frequency',
                           'payment_value': 'MonetaryValue'}, inplace=True)
    return df_rfm

def create_seller_df(df) :
    # Konversi kolom ke datetime
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    monthly_seller_df = df.resample(rule='M', on='order_approved_at').seller_id.nunique()
    monthly_seller_df = monthly_seller_df.reset_index()
    monthly_seller_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    monthly_seller_df['order_approved_at']=pd.to_datetime(monthly_seller_df['order_approved_at'])
    monthly_seller_df['month-year'] = monthly_seller_df['order_approved_at'].dt.strftime('%b') + '-' + \
                                      monthly_seller_df['order_approved_at'].dt.strftime('%Y')

    return monthly_seller_df


all_df=pd.read_csv('all_df.csv')
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()


with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/RandyDz/Olist-e-commerce/4252eb2380a48e795dbad8477e0fa6738f4321e4/St%C3%BAdio__1_-removebg-preview.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items(main_df)
bystate_df = create_bystate(all_df)
rfm_df = create_rfm_df(main_df)
sellers_df=create_seller_df(main_df)

st.header('Brazillian e-Commerce Dashboard :sparkles:')

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR')
    st.metric("Total Revenue", value=total_revenue)

#=======================================================Daily orders=================================
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)
#=======================================================Best & Worst Performing Product=================================
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=20)
plt.show()
st.pyplot(fig)

#=======================================================Customers demography=================================
st.subheader("Customer by State")
fig,ax=plt.subplots(figsize=(20, 10))
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    color="#72BCD4"
)
plt.title("Number of Customer by States", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)
plt.show()
st.pyplot(fig)

#=======================================================Active Seller Growth=================================
st.subheader("Number of Active Sellers")
fig,ax=plt.subplots(figsize=(15,6))
sns.lineplot(data=sellers_df, x='month-year', y='seller_count', marker='o')
plt.title('Number of Sellers per Month', fontsize=20)
plt.xlabel('Month-Year',fontsize=18)
plt.ylabel('Number of Sellers',fontsize=16)
plt.xticks(rotation=45)
sns.lineplot(data=sellers_df, x='month-year', y='seller_count', marker='o')
plt.ylabel('Number of Sellers',fontsize=16)
plt.show()
st.pyplot(fig)







#=======================================================Best Customer Based on RFM Parameters=================================
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.MonetaryValue.mean(), "BRL", locale='pt_BR')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="Recency", x="customer_unique_id", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15, rotation=90)

sns.barplot(y="Frequency", x="customer_unique_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15,rotation=90)

sns.barplot(y="MonetaryValue", x="customer_unique_id", data=rfm_df.sort_values(by="MonetaryValue", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15, rotation=90)

plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
plt.show()
st.pyplot(fig)
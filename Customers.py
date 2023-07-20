import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple
from datetime import date
import io
import folium 

## customize the layout of matplotlib.pyplot plots
plt.style.use('ggplot')
## Set the width to the full screen
st.set_page_config(layout="wide")

# DOWNLOAD the dataset df
# @st.cache
def get_data(): 
    df= pd.read_csv('bicycle_dataset.csv')
    # Drop the column 'Unnamed: 0'
    df = df.drop('Unnamed: 0', axis=1)
    return df

# @st.cache
# def convert_df(df):
#     # IMPORTANT: Cache the conversion to prevent computation on every rerun
#     return df.to_csv().encode('utf-8')

# csv = convert_df(my_large_df)
# st.download_button(
#     label="Download data as CSV",
#     data=csv,
#     file_name='large_df.csv',
#     mime='text/csv',
# )
# DOWNLOAD the dataset filtered_data
# @st.cache
def get_filtered_data (df, selected_month, selected_countries, selected_statuses):
    filtered_data = df.copy()
    if selected_statuses == 'all' and selected_month != 'all' and selected_countries != 'all': 
        filtered_data= filtered_data[filtered_data['order_status'] != 'all']
        filtered_data= df[(df['month'] == selected_month) & (df['state'] == selected_countries)]
        return filtered_data
    elif selected_countries == 'all' and selected_month != 'all' and selected_statuses != 'all':
        filtered_data= filtered_data[filtered_data['state'] != 'all']
        filtered_data = df[(df['month'] == selected_month) & (df['order_status'] == selected_statuses)]
        return filtered_data
    elif selected_month == 'all' and selected_countries != 'all' and selected_statuses != 'all':
        filtered_data= filtered_data[filtered_data['month'] != 'all']
        filtered_data = df[(df['order_status'] == selected_statuses) & (df['state'] == selected_countries)]
        return filtered_data
    elif selected_month == 'all' and selected_countries == 'all' and selected_statuses != 'all': 
        filtered_data= filtered_data[(filtered_data['month'] != 'all') & (filtered_data['state'] != 'all')]
        filtered_data = df[df['order_status'] == selected_statuses]
        return filtered_data
    elif selected_month == 'all' and selected_statuses == 'all' and selected_countries != 'all':
        filtered_data= filtered_data[(filtered_data['month'] != 'all') & (filtered_data['order_status'] != 'all')]
        filtered_data = df[df['state'] == selected_countries]
        return filtered_data
    elif selected_countries == 'all' and selected_statuses == 'all' and selected_month != 'all':
        filtered_data= filtered_data[(filtered_data['state'] != 'all') & (filtered_data['order_status'] != 'all')]
        filtered_data = df[df['month'] == selected_month]
        return filtered_data
    elif selected_month == 'all' and selected_countries == 'all' and selected_statuses == 'all':
        filtered_data= filtered_data[(filtered_data['month'] != 'all') & (filtered_data['state'] != 'all') & (filtered_data['order_status'] != 'all')]
        return filtered_data
    else: 
        filtered_data = filtered_data[(filtered_data['month'] == selected_month) & (filtered_data['state'] == selected_countries) & (filtered_data['order_status']== selected_statuses)]
        return filtered_data

# Get the previous month
def get_previous_month(selected_month):
    if selected_month == 'all' or selected_month == 1:
        previous_month = selected_month
    else: 
        previous_month = selected_month -1
    return previous_month
# Dataset for maps
## overview
# @st.cache
def get_data_map_overview(filtered_data):
    filtered_data = filtered_data[['lat', 'long']]
    # Rename the "long" column to "lon"
    filtered_data = filtered_data.rename(columns={"long": "lon"})
    return filtered_data


## DOWNLOAD the selected dataset in csv
# @st.cache
def download_filtered_data_csv(df, selected_month, selected_countries, selected_statuses):
    filtered_data = get_filtered_data (df, selected_month, selected_countries, selected_statuses)
    # # Dropping rows with 'all' values in specified columns
    # filtered_data = filtered_data[(filtered_data['month'] != 'all') & (filtered_data['state'] != 'all') & (filtered_data['order_status'] != 'all')]
    current_date = date.today().strftime("%Y-%m-%d")
    file_name_csv = f"BicycleStoreAustralia2017_month_{selected_month}_state_{selected_countries}_order_status_{selected_statuses}_saved_{current_date}.csv"
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    return [csv, file_name_csv]

## DOWNLOAD the selected dataset in excel
# @st.cache
# def download_filtered_data_excel(df, selected_month, selected_countries, selected_statuses):
#     filtered_data = get_filtered_data (df, selected_month, selected_countries, selected_statuses)
#     # # Dropping rows with 'all' values in specified columns
#     # filtered_data = filtered_data[(filtered_data['month'] != 'all') & (filtered_data['state'] != 'all') & (filtered_data['order_status'] != 'all')]
#     current_date = date.today().strftime("%Y-%m-%d")
#     file_name_excel = f"BicycleStoreAustralia2017_month_{selected_month}_state_{selected_countries}_order_status_{selected_statuses}_saved_{current_date}.xlsx"
#     # Save the filtered data to an Excel file
#     filtered_data.to_excel(file_name_excel, index=False)
#     # Read the Excel data as bytes
#     excel_bytes = io.BytesIO()
#     with pd.ExcelWriter(excel_bytes, engine='xlsxwriter') as writer:
#         filtered_data.to_excel(writer, index=False)
#     return [excel_bytes.getvalue(), file_name_excel]

###########KPI metrics#############
# Create KPI metrics 
def calculate_kpis(filtered_data):
    total_sales = filtered_data['list_price'].sum()
    sales_in_m = f"{total_sales / 1000000:.2f}M"
    total_orders = filtered_data['transaction_id'].nunique()
    average_sales_per_order = f"{total_sales / total_orders / 1000:.2f}K"
    unique_customers = filtered_data['customer_id'].nunique()
    return [sales_in_m, total_sales, total_orders, average_sales_per_order, unique_customers]

# Create KPI metrics previous sales
def calculate_sales_previous(previous_data, total_sales):
    total_sales_previous = previous_data['list_price'].sum()
    difference_sales = total_sales - total_sales_previous
    percentage_difference = (difference_sales / total_sales_previous) * 100
    return f"{percentage_difference:.1f}%"
# Create KPI metrics previous orders
def calculate_orders_previous(previous_data, total_orders):
    total_orders_previous = previous_data['transaction_id'].nunique()
    difference_orders = total_orders - total_orders_previous
    percentage_difference = (difference_orders / total_orders_previous) * 100
    return f"{percentage_difference:.1f}%"
# Create KPI metrics previous average_sales_orders
def calculate_average_sales_orders_previous(previous_data, total_sales, total_orders):
    average_sales_per_order = total_sales / total_orders
    total_sales_previous = previous_data['list_price'].sum()
    total_orders_previous = previous_data['transaction_id'].nunique()
    average_sales_per_order_previous = total_sales_previous / total_orders_previous
    difference_average_sales_orders = average_sales_per_order - average_sales_per_order_previous
    percentage_difference = (difference_average_sales_orders  / average_sales_per_order_previous) * 100
    return f"{percentage_difference:.1f}%"
# Create KPI metrics previous customer unique
def calculate_customers_previous(previous_data, unique_customers):
    unique_customers_previous = previous_data['customer_id'].nunique()
    difference_unique_customers = unique_customers - unique_customers_previous
    percentage_difference = (difference_unique_customers / unique_customers_previous) * 100
    return f"{percentage_difference:.1f}%"


# Display sidebar and filters
def display_sidebar(df):
    st.sidebar.header("Filters")
    # Modify the unique values for month, state, and order_status columns
    months = ['all'] + df['month'].unique().tolist()
    selected_month = st.sidebar.selectbox('Select Month', months)
    
    states = ['all'] + df['state'].unique().tolist()
    selected_countries = st.sidebar.selectbox("Select State", states)
    
    statuses = ['all'] + df['order_status'].unique().tolist()
    selected_statuses = st.sidebar.selectbox("Select Order Status", statuses)
    
    return selected_month, selected_countries, selected_statuses

###CUSTOMERS map -> Customers | The best and worst customers#####
# Get my computed difference score
def get_my_computed_CLV(df):
    df['order_status'] = df['order_status'].map({'Approved': 0, 'Cancelled': 1})
    
    # Group the DataFrame by 'customer_id' and 'brand', and count the number of occurrences.
    brand_counts = df.groupby(['customer_id', 'brand']).size().reset_index(name='count')
    # Group the 'brand_counts' DataFrame by 'customer_id' and create a list of unique brands for each customer.
    customer_brands = brand_counts.groupby('customer_id')['brand'].unique()
    # Create a new column 'purchased_brands' in the original DataFrame and assign the unique brands to each customer.
    df['purchased_brands'] = df['customer_id'].map(customer_brands)
    # Group the 'brand_counts' DataFrame by 'customer_id' and count the number of unique brands for each customer.
    customer_brand_counts = brand_counts.groupby('customer_id')['brand'].count()
    # Create a new column 'num_purchased_brands' in the original DataFrame and assign the number of purchased brands to each customer.
    df['num_purchased_brands'] = df['customer_id'].map(customer_brand_counts)
    
    product_line_counts = df.groupby(['customer_id', 'product_line']).size().reset_index(name='count')
    customer_product_line = product_line_counts.groupby('customer_id')['product_line'].unique()
    df['purchased_product_line'] = df['customer_id'].map(customer_product_line)
    customer_product_line_counts = product_line_counts.groupby('customer_id')['product_line'].count()
    df['num_purchased_product_line'] = df['customer_id'].map(customer_product_line_counts)
    

    customer_stats = df.groupby('customer_id').agg({'transaction_id': 'count', 'list_price': 'sum', 'online_order': 'sum', 'owns_car': 'first', 'age_range': 'first', 'age': 'first', 'order_status': 'sum', 'purchased_brands': 'first', 'num_purchased_brands': 'first', 'purchased_product_line': 'first', 'num_purchased_product_line': 'first', 'state': 'first'})
    customer_stats.columns = ['transaction_count', 'total_list_price', 'online_order_count', 'owns_car', 'age_range', 'age', 'order_status', 'purchased_brands', 'num_purchased_brands', 'purchased_product_line', 'num_purchased_product_line', 'state']
    customer_stats['offline_order_count'] = customer_stats['transaction_count'] - customer_stats['online_order_count']
    customer_stats['difference_score'] = customer_stats['total_list_price'] - (customer_stats['transaction_count']*200)
    customer_stats = customer_stats.sort_values('difference_score', ascending=False)
    # Determine the group labels using cut() function
    num_groups = 5  # Number of groups
    bins = np.linspace(customer_stats['difference_score'].min(), customer_stats['difference_score'].max(), num_groups + 1)
    labels = range(1, num_groups + 1)
    customer_stats['difference_score_group'] = pd.cut(customer_stats['difference_score'], bins=bins, labels=labels, include_lowest=True)

    # Add 'lat' and 'long' columns
    lat_long_data = {'customer_id': [], 'lat': [], 'long': []}
    for customer_id, row in customer_stats.iterrows():
        customer_data = df[df['customer_id'] == customer_id]
        lat = customer_data['lat'].values[0]
        long = customer_data['long'].values[0]
        lat_long_data['customer_id'].append(customer_id)
        lat_long_data['lat'].append(lat)
        lat_long_data['long'].append(long)
    
    lat_long_df = pd.DataFrame(lat_long_data)
    customer_stats = pd.merge(customer_stats, lat_long_df, on='customer_id', how='left')
    return customer_stats


# MAP FOR ALL CLV score
def get_map_difference_score_all(df_1, df_2):
    df_customers = df_1[["customer_id", "difference_score"]]
    df_lat_long = df_2[['customer_id', 'lat', 'long']]
    df_lat_long = df_lat_long.drop_duplicates(subset=['customer_id'])
    df_all= pd.merge(df_customers, df_lat_long, on='customer_id')
    min_price_all = df_all["difference_score"].min()
    max_price_all = df_all["difference_score"].max()
    # Create a map centered at a specific location
    m = folium.Map(location=[-37.8136, 144.9631], width="100%", height="100%")
    colormap = {
    (min_price_all, 3248): 'red',       # List prices between min_price and 500 will be green
    (3249, 4819): 'orange',           # List prices between 500 and 1000 will be yellow
    (4820, 6588): 'yellow',
    (6588, max_price_all): 'green'         # List prices between 1500 and max_price will be red
    }
    for loc, p in zip(zip(df_all["lat"], df_all["long"]), df_all["difference_score"]): 
        # Determine the color based on price range
        color = next((color for price_range, color in colormap.items() if price_range[0] < p <= price_range[1]), 'green')     
        folium.Circle(
            location=loc,
            radius=10,
            fill=True,
            color=color
        ).add_to(m)
    # Convert the Folium map to HTML string
    map_html = m.get_root().render()
    return map_html
# MAP FOR GREEN CLV SCORE
def get_map_difference_score_best(df_1, df_2):
    df_customers = df_1[["customer_id", "difference_score"]]
    df_lat_long = df_2[['customer_id', 'lat', 'long']]
    df_lat_long = df_lat_long.drop_duplicates(subset=['customer_id'])
    df_all= pd.merge(df_customers, df_lat_long, on='customer_id')
    max_price = df_all["difference_score"].max()
    sorted_df = df_all.sort_values('difference_score', ascending = False)
        # Group the data by 'customer_id' and get the first two orders for each customer
    df_all = sorted_df

    # Create a map centered at a specific location
    m = folium.Map(location=[-37.8136, 144.9631], width="100%", height="100%")

    for loc, p in zip(zip(df_all["lat"], df_all["long"]), df_all["difference_score"]):
        # Display only green dots based on price range
        if 6588 < p <= max_price:
            folium.Circle(
                location=loc,
                radius=10,
                fill=True,
                color='green'
            ).add_to(m)

    # Convert the Folium map to HTML string
    map_html = m.get_root().render()
    return map_html
# MAP FOR YELLOW CLV SCORE
def get_map_difference_score_average_yellow(df_1, df_2):
    df_customers = df_1[["customer_id", "difference_score"]]
    df_lat_long = df_2[['customer_id', 'lat', 'long']]
    df_lat_long = df_lat_long.drop_duplicates(subset=['customer_id'])
    df_all= pd.merge(df_customers, df_lat_long, on='customer_id')
    # Create a map centered at a specific location
    m = folium.Map(location=[-37.8136, 144.9631], width="100%", height="100%")

    for loc, p in zip(zip(df_all["lat"], df_all["long"]), df_all["difference_score"]):
        # Display only green dots based on price range
        if 4820 < p <= 6588:
            folium.Circle(
                location=loc,
                radius=10,
                fill=True,
                color='yellow'
            ).add_to(m)

    # Convert the Folium map to HTML string
    map_html = m.get_root().render()
    return map_html
# MAP FOR ORANGE CLV SCORE
def get_map_difference_score_average_orange(df_1, df_2):
    df_customers = df_1[["customer_id", "difference_score"]]
    df_lat_long = df_2[['customer_id', 'lat', 'long']]
    df_lat_long = df_lat_long.drop_duplicates(subset=['customer_id'])
    df_all= pd.merge(df_customers, df_lat_long, on='customer_id')
    # Create a map centered at a specific location
    m = folium.Map(location=[-37.8136, 144.9631], width="100%", height="100%")

    for loc, p in zip(zip(df_all["lat"], df_all["long"]), df_all["difference_score"]):
        # Display only green dots based on price range
        if 3249 < p <= 4819:
            folium.Circle(
                location=loc,
                radius=10,
                fill=True,
                color='orange'
            ).add_to(m)

    # Convert the Folium map to HTML string
    map_html = m.get_root().render()
    return map_html
# MAP FOR RED CLV SCORE
def get_map_difference_score_low(df_1, df_2):
    df_customers = df_1[["customer_id", "difference_score"]]
    df_lat_long = df_2[['customer_id', 'lat', 'long']]
    df_lat_long = df_lat_long.drop_duplicates(subset=['customer_id'])
    df_all= pd.merge(df_customers, df_lat_long, on='customer_id')
    min_price = df_all["difference_score"].min()
    sorted_df = df_all.sort_values('difference_score', ascending = True)
        # Group the data by 'customer_id' and get the first two orders for each customer
    df_all = sorted_df
    # Create a map centered at a specific location
    m = folium.Map(location=[-37.8136, 144.9631], width="100%", height="100%")

    for loc, p in zip(zip(df_all["lat"], df_all["long"]), df_all["difference_score"]):
        # Display only green dots based on price range
        if min_price <= p < 3248:
            folium.Circle(
                location=loc,
                radius=10,
                fill=True,
                color='red'
            ).add_to(m)

    # Convert the Folium map to HTML string
    map_html = m.get_root().render()
    return map_html


####CUSTOMERS new old reactive
def calculate_customer_stats(df):
    # Sort the data by month and customer_id
    df.sort_values(['month', 'customer_id'], inplace=True)

    # Create a new column 'previous_month' to store the previous month for each customer
    df['previous_month'] = df.groupby('customer_id')['month'].shift()

    # Group the data by month
    grouped_data = df.groupby('month')

    new_customers_list = []
    reactive_customers_list = []
    total_customers_list = []

    # Iterate over each month group
    for month, group in grouped_data:
        # Identify new customers by comparing the current month with the previous month
        new_customers = group[~group['customer_id'].isin(group[group['month'] == group['previous_month']]['customer_id'])]['customer_id'].nunique()

        # Identify reactive customers who ordered in the previous month
        reactive_customers = group[group['month'] == group['previous_month']]['customer_id'].nunique()

        # Calculate the total number of customers
        total_customers = group['customer_id'].nunique()

        new_customers_list.append(new_customers)
        reactive_customers_list.append(reactive_customers)
        total_customers_list.append(total_customers)

    return new_customers_list, reactive_customers_list, total_customers_list

def plot_customer_analysis(new_customers_list, reactive_customers_list, total_customers_list):
    months = range(1, 13)
    bar_width = 0.3

    new_customers_pos = [x - bar_width for x in months]
    reactive_customers_pos = months
    total_customers_pos = [x + bar_width for x in months]

    plt.bar(new_customers_pos, new_customers_list, width=bar_width, color='green', label='New Customers')
    plt.bar(reactive_customers_pos, reactive_customers_list, width=bar_width, color='violet', label='Reactive Customers')
    plt.bar(total_customers_pos, total_customers_list, width=bar_width, color='gray', label='Total Customers')

    plt.xlabel('Month')
    plt.ylabel('Number of Customers')
    plt.title('Customer Analysis')
    plt.legend()

    plt.show()
############MAIN FUNCTION###########
def main():
    ## Set title and subtitle
    st.title("📊 Customers Dashboard")
    st.caption("Bicycle Store (Australia, 2017)")
    st.caption("Data source: https://www.kaggle.com/datasets/rohitsahoo/bicycle-store-dataset")

    df = get_data()
    
    selected_month, selected_countries, selected_statuses = display_sidebar(df)
    filtered_data = get_filtered_data(df, selected_month, selected_countries, selected_statuses)
    previous_month = get_previous_month(selected_month)
    previous_data = get_filtered_data(df, previous_month, selected_countries, selected_statuses)
    sales_in_m, total_sales, total_orders, average_sales_per_order, unique_customers = calculate_kpis(filtered_data)

    
    ####################TABS######################
    # create 3 tabs for better overview
    tabs = st.tabs(['metrics', 'map', 'characteristics', 'CLV', 'RFM'])
    
###METRICS
    tab_metrics = tabs[0]
    csv, file_name_csv = download_filtered_data_csv(filtered_data, selected_month, selected_countries, selected_statuses)
    # excel_bytes, file_name_excel = download_filtered_data_excel(filtered_data, selected_month, selected_countries, selected_statuses)
    with tab_metrics:
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Sales", sales_in_m, calculate_sales_previous(previous_data, total_sales))
        with cols[1]:
            st.metric("Total Orders", total_orders, calculate_orders_previous(previous_data, total_orders))
        with cols[2]:
            st.metric("Average Sales per Order", average_sales_per_order, calculate_average_sales_orders_previous(previous_data, total_sales, total_orders))
        with cols[3]:
            st.metric("Unique Customers", unique_customers, calculate_customers_previous(previous_data, unique_customers))

        cols = st.columns(1)
        with cols[0]: 
            st.download_button(
                label="Download filtered data as CSV",
                data= csv,
                file_name= file_name_csv,
                mime="text/csv",
                key='download-csv'
                )
        # with cols[1]:
        #     st.download_button(
        #         label="Download filtered data as Excel",
        #         data=excel_bytes,
        #         file_name=file_name_excel,
        #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #         key='download-excel'
        #         ) 
        cols = st.columns(1)
        with cols[0]: 
            st.table(filtered_data.head(10))
            
###MAP
    df_map_overview = get_data_map_overview(filtered_data)
    tab_map = tabs[1]
    with tab_map: 
        cols = st.columns(1)
        with cols[0]:
            st.markdown('Selected Filter')
            st.map(df_map_overview)
                
###CHARACTERISTICS
    tab_characteristics = tabs[2]
    with tab_characteristics:
        cols = st.columns(1)
        with cols[0]:
            st.write('Overview')
        cols = st.columns(3)
        with cols[0]:
            st.image('customers_pie_chart_state.png')
        with cols[1]:
            st.image('customers_pie_chart_gender.png')
        with cols[2]: 
            st.image('customers_pie_chart_car.png')

        cols = st.columns(2)
        with cols[0]:
            st.image('customers_bar_chart_age_group.png')
        with cols[1]:
            st.image('customers_waffle_chart_job_industry.png')
        
        cols = st.columns(1)
        with cols[0]:
            st.image('customers_bar_chart_new_total.png')
        
        cols = st.columns(1)
        with cols[0]:
            st.write('Offline vs. Online')
        cols = st.columns(2)
        with cols[0]:
            st.image('customers_pie_chart_online_offline_orders.png')
        with cols[1]:
            st.image('customers_bar_chart_online_offline.png')
            
        cols = st.columns(1)
        with cols[0]:
            st.write('Order')    
        cols = st.columns(2)
        with cols[0]:
            st.image('customers_pie_chart_frequency_of_ordering.png')
        with cols[1]:
            st.image('customers_pie_chart_timespan.png')
    
###CLV
    tab_clv = tabs[3]
    customer_stats = get_my_computed_CLV(df)
    map_html = get_map_difference_score_all(customer_stats, filtered_data)
    map_html_difference_score_best = get_map_difference_score_best(customer_stats, filtered_data)
    map_html_difference_score_average_orange= get_map_difference_score_average_orange(customer_stats, filtered_data)
    map_html_difference_score_average_yellow= get_map_difference_score_average_yellow(customer_stats, filtered_data)
    map_html_difference_score_low = get_map_difference_score_low(customer_stats, filtered_data)
    with tab_clv: 
        cols = st.columns(1)
        with cols[0]:
            chart = st.radio(
    "Select the CLV score that you would like to display",
    ('All', 'Best CLV Score', '25 % - 50 % CLV Score', '50 % - 75 % CLV Score', 'Low CLV Score'))
            if chart == 'All':
                st.components.v1.html(map_html, width= 800, height= 300)
            if chart == 'Best CLV Score':
                st.components.v1.html(map_html_difference_score_best, width= 800, height= 300)        
            if chart == '25 % - 50 % CLV Score':
                st.components.v1.html(map_html_difference_score_average_orange, width= 800, height= 300)
            if chart == '50 % - 75 % CLV Score':
                st.components.v1.html(map_html_difference_score_average_yellow, width= 800, height= 300)
            if chart == 'Low CLV Score':
                st.components.v1.html(map_html_difference_score_low, width= 800, height= 300)
            
###RFM   
    tab_rfm = tabs[4]
    with tab_rfm:
        cols = st.columns(3)   
        with cols[0]:
            st.image('rfm_cluster_recency_4.png')
        with cols[1]:
            st.image('rfm_cluster_frequency_4.png')  
        with cols[2]:
            st.image('rfm_cluster_monetary_4.png')
        cols = st.columns(1)
        with cols[0]:
            st.write('**Cluster 0| New Customers - new customers promotion | 22.7 %**')
            st.write('This particular cluster comprises of users who are new to the platform. These users possess the potential to evolve into long-term consumers with a high frequency of usage and significant monetary value. To foster brand loyalty, it is recommended to target them specifically with tailored "new-customer promotions".')
            
            st.write('**Cluster 1 and 2| Old Customers**')
            st.write('Customers in this segment have previously displayed a high frequency of purchases. However, they have ceased visiting the platform for reasons unknown and have not been observed making recent purchases on the site. This could imply various scenarios, such as their dissatisfaction with the service leading them to switch to a competitor platform or a loss of interest in the products offered.')
            
            st.write('**Cluster 1 | Old Customers | 20.1 %**')
            st.write('These customers frequently make purchases, but haven`t recently visited the platform. Their monetary value is exceptionally high, suggesting that they tend to spend a significant amount when shopping. This indicates that users in this segment are likely to engage in multiple purchases within a single order and are highly receptive to cross-selling and up-selling techniques. Additionally, it is possible that this segment includes resellers who make bulk purchases of products.')
            
            st.write('**Cluster 2 | Old Customers | 28.0 %**')
            st.write('These customers have not made any recent purchases. Previously, they used to buy frequently and spend a lot of money.')
            
            st.write('**Cluster 3 | Old Customers | 29.3 %**')
            st.write('These customers have not made any recent purchases. In the past, they used to buy frequently and spend a small amount of money.')
  
        cols = st.columns(1)
        with cols[0]:
            st.write('Elbow Methode')
            st.image('rfm_cluster_elbow.png')
            st.write('silhouette_score = 0.2885960017094719')
            
###report power point and word 
    # tab_report = tabs[5]
    # with tab_report:
    #     cols = st.columns(1)        
    #     with cols[0]:
    #         st.write('Hello world!')         
        # with cols[0]:
        #     st.download_button(
        #         label="Download filtered data as Word document",
        #         data=word_doc_bytes,
        #         file_name=file_name,
        #         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        #         key='download-docx'
        #     )
        # with cols[1]:
        #     st.download_button(
        #         label="Download filtered data as Power Point"
        #         data=,
        #         file_name=,
        #         mime=,
        #         key=
        #     )
        
if __name__ == '__main__':
    main()






import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings(action='ignore')

@st.cache(allow_output_mutation=True)
def get_data():
    url = 'https://api.covid19india.org/csv/latest/state_wise.csv'
    return pd.read_csv(url)
    
df = get_data()

st.title('COVID-19 Outbreak Monitor')
st.markdown("> and then the whole world walked inside and shut their doors and said we will stop it.")

# Status Table
st.header('\n')
@st.cache(allow_output_mutation=True)
def display_status(df):
    df = df[['State', 'Confirmed', 'Recovered', 'Active', 'Deaths', 'Last_Updated_Time']]
    df.drop([0], axis=0, inplace=True)
    df = df.style.background_gradient(cmap="YlGnBu")
    return df

status_table = display_status(df)
st.dataframe(status_table)


# Status of COVID-19
summary = df[df['State'] == 'Total']
summary = summary[['Active', 'Recovered', 'Deaths']]
summary = summary.transpose()
summary = summary.reset_index()
summary = summary.rename(columns = {'index' : 'Property', 0 : 'Numbers'})

fig_summary = px.pie(summary,
                     values='Numbers',
                     names='Property')
st.plotly_chart(fig_summary)

# Statewise distribution of confirmed, active, recovered and deceased
st.header('Cases Distribution')
statewise = df.drop([0])

status = ['Confirmed', 'Active', 'Recovered', 'Deaths']
option = st.selectbox('', 
                    status)
@st.cache(allow_output_mutation=True)
def display_status(option):
    df = statewise[['State', option]]
    fig = px.pie(df,
                 values=option,
                 names='State')
    fig.update_traces(hoverinfo='label+percent+name', textinfo='none')
    return fig
status = display_status(option)
st.plotly_chart(status)

# Spread Trends
st.header('Spread Trends')

@st.cache(allow_output_mutation=True)
def get_trends_data():
    url = 'https://api.covid19india.org/csv/latest/state_wise_daily.csv'
    return pd.read_csv(url)
trends = get_trends_data()
 
trends = trends.rename(columns = {'TT' : 'All States',
                          'AN' : 'Andaman and Nicobar Islands',
                          'AP' : 'Andhra Pradesh',
                          'AR' : 'Arunachal Pradesh',
                          'AS' : 'Assam',
                          'BR' : 'Bihar',
                          'CH' : 'Chandigarh',
                          'CT' : 'Chhattisgarh',
                          'DN' : 'Dadar and Nagar Haveli',
                          'DD' : 'Daman and Diu',
                          'DL' : 'Delhi', 
                          'GA' : 'Goa',
                          'GJ' : 'Gujarat',
                          'HR' : 'Haryana',
                          'HP' : 'Himachal Pradesh',
                          'JK' : 'Jammu and Kashmir',
                          'JH' : 'Jharkhand',
                          'KA' : 'Karnataka', 
                          'KL' : 'Kerala',
                          'LA' : 'Ladakh',
                          'LD' : 'Lakshdweep',
                          'MP' : 'Madhya Pradesh',
                          'MH' : 'Maharastra',
                          'MN' : 'Manipur',
                          'ML' : 'Meghalaya',
                          'MZ' : 'Mizoram',
                          'NL' : 'Nagaland',
                          'OR' : 'Odisa',
                          'PY' : 'Puducherry',
                          'PB' : 'Punjab', 
                          'RJ' : 'Rajasthan',
                          'SK' : 'Sikkim',
                          'TN' : 'Tamil Nadu',
                          'TG' : 'Telangana', 
                          'TR' : 'Tripura',
                          'UP' : 'Uttar Pradesh',
                          'UT' : 'Uttarakhand',
                          'WB' : 'West Bengal'})

log = st.checkbox('Logarithmic')
cumulative = st.checkbox('Cumulative')

trends_confirmed = trends[trends['Status'] == 'Confirmed'].drop(columns = ['Status'])
trends_recovered = trends[trends['Status'] == 'Recovered'].drop(columns = ['Status'])
trends_deceased = trends[trends['Status'] == 'Deceased'].drop(columns = ['Status'])

if cumulative:
    trends_confirmed = trends_confirmed.set_index('Date')
    trends_confirmed = trends_confirmed.cumsum()
    trends_confirmed = trends_confirmed.reset_index()

    trends_recovered = trends_recovered.set_index('Date')
    trends_recovered = trends_recovered.cumsum()
    trends_recovered = trends_recovered.reset_index()

    trends_deceased = trends_deceased.set_index('Date')
    trends_deceased = trends_deceased.cumsum()
    trends_deceased = trends_deceased.reset_index()


@st.cache(allow_output_mutation=True)
def trends_plot(state, df):
    df = df[['Date', state]]
    if log:
        fig = go.Figure(data=go.Scatter(x=df['Date'],
                                        y=np.log1p(df[state]),
                                        mode='lines+markers'))
    else:
        fig = go.Figure(go.Scatter(x=df['Date'],
                                   y=df[state],
                                   mode='lines+markers'))
        
    fig.update_layout(xaxis_title='----->Timeline',
                        yaxis_title='----->Patients')
    return fig

x = list(trends_confirmed.columns)
del x[0]
del x[-1]

states =  x
option_c = st.selectbox('Confirmed Cases',states)
confirmed = trends_plot(option_c, trends_confirmed)
st.plotly_chart(confirmed)

option_r = st.selectbox('Recovered Cases',states)
recovered = trends_plot(option_r, trends_recovered)
st.plotly_chart(recovered)

option_d = st.selectbox('Number of Deceased',states)
deceased = trends_plot(option_d, trends_deceased)
st.plotly_chart(deceased)


# comparison

st.header('Compare')

cases = ['Confirmed Cases', 'Recovered Cases', 'Deceased Cases']
cmp = st.selectbox('I want to compare', cases)
state_1 = st.selectbox('in', x)
state_2 = st.selectbox('and', x)

@st.cache(allow_output_mutation=True)
def compare(df, state_1, state_2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'],
                             y=df[state_1],
                             mode='lines+markers',
                             name=state_1))
    fig.add_trace(go.Scatter(x=df['Date'],
                             y=df[state_2],
                             mode='lines+markers',
                             name=state_2))
    return fig

if cmp == cases[0]:
    trends_confirmed = trends_confirmed.set_index('Date')
    trends_confirmed = trends_confirmed.cumsum()
    trends_confirmed = trends_confirmed.reset_index()
    fig_cmp = compare(trends_confirmed, state_1, state_2)
    
elif cmp == cases[1]:
    trends_recovered = trends_recovered.set_index('Date')
    trends_recovered = trends_recovered.cumsum()
    trends_recovered = trends_recovered.reset_index()
    fig_cmp = compare(trends_recovered, state_1, state_2)

else:
    trends_deceased = trends_deceased.set_index('Date')
    trends_deceased = trends_deceased.cumsum()
    trends_deceased = trends_deceased.reset_index()
    fig_cmp = compare(trends_deceased, state_1, state_2)
    
st.plotly_chart(fig_cmp)


# Testing
st.header('COVID-19 Testing Status')

@st.cache(allow_output_mutation=True)
def get_test_data():
    url = 'https://api.covid19india.org/csv/latest/tested_numbers_icmr_data.csv'
    return pd.read_csv(url)

test = get_test_data()
tested_pm = test.copy()

test = test[['Update Time Stamp', 'Total Samples Tested']]
test = test.set_index('Update Time Stamp')
test = test.diff()
test = test.reset_index()
test['Update Time Stamp'] = pd.to_datetime(test['Update Time Stamp'])
test['Update Time Stamp'] = test['Update Time Stamp'].dt.strftime('%d-%m-%Y')
test['Date'] = pd.DatetimeIndex(test['Update Time Stamp']).date
test['Month'] = pd.DatetimeIndex(test['Update Time Stamp']).month
test = test[['Date', 'Month', 'Total Samples Tested']]
test = test.fillna(0)

st.markdown('\n')
st.markdown('**Samples tested daily**')

def test_plot(df):
    fig = px.scatter(df,
                    x = 'Date',
                    y = 'Total Samples Tested',
                    color = 'Month',
                    hover_data = ['Date', 'Total Samples Tested'],
                    size = 'Total Samples Tested')
    fig.update_layout(xaxis_title='-----> Timeline',
                      yaxis_title='-----> Number of Tests')
    st.plotly_chart(fig)

test_plot(test)

st.markdown('**Tests per million**')
tested_pm = tested_pm[['Update Time Stamp', 'Tests per million']]
tested_pm['Date'] = pd.to_datetime(tested_pm['Update Time Stamp'])
tested_pm['Date'] = tested_pm['Date'].dt.strftime('%d-%m-%Y')
tested_pm['Month'] = pd.DatetimeIndex(tested_pm['Date']).month
tested_pm = tested_pm.fillna(0)
tested_pm.rename(columns = {'Tests per million':'Total Samples Tested'}, inplace = True)

test_plot(tested_pm)

# Hospital Data
st.header('Hospitals')

def get_hospital_data():
    url = 'https://api.rootnet.in/covid19-in/hospitals/beds.json'
    hosp = pd.read_json(url)
    return pd.DataFrame(hosp['data']['regional'])

hosp = get_hospital_data()
hosp = hosp[hosp['state'] != 'INDIA'] 
    
def urban_rural(hosp, x, y, name):
    fig = go.Figure(data=[
        go.Bar(name=name,
                x=x, 
                y=y)
    ])
    fig.update_layout(barmode='group')
    st.plotly_chart(fig)
    
def ur_plot(hosp, y_urban, y_rural, name_urban, name_rular):
    fig = go.Figure(data=[
        go.Bar(name=name_urban, x=hosp['state'], y=y_urban),
        go.Bar(name=name_rular, x=hosp['state'], y=y_rural)
    ])
    fig.update_layout(barmode='group')
    st.plotly_chart(fig)
    
urban_button = st.button('Urban Hospital')
if urban_button:
    urban_rural(hosp, hosp['state'], hosp['urbanHospitals'], 'Urban Hospital')
else:
    pass

rural_button = st.button('Rural Hospital')
if rural_button:
    urban_rural(hosp, hosp['state'], hosp['ruralHospitals'], 'Rural Hospital')
else:
    pass

ur_button = st.button('Urban VS Rural Hospital')
if ur_button:
    ur_plot(hosp, hosp['urbanHospitals'], hosp['ruralHospitals'], 'Urban Hospital', 'Rural Hospital')
else:
    pass

# Hospital Beds
st.header('Hospital Beds')

urbanbeds_button = st.button('Urban Beds')
if urbanbeds_button:
    urban_rural(hosp, hosp['state'], hosp['urbanBeds'], 'Urban Hospital Beds')
else:
    pass

ruralbeds_button = st.button('Rural Beds')
if ruralbeds_button:
    urban_rural(hosp, hosp['state'], hosp['ruralBeds'], 'Rural Hospital Beds')
else:
    pass

urbeds_button = st.button('Urban vs Rural Beds')
if urbeds_button:
    ur_plot(hosp, hosp['urbanBeds'], hosp['ruralBeds'], 'Urban Hospital Beds', 'Rural Hospital Beds')
else:
    pass

# Map
# @st.cache
# def on_map():
#     url = 'https://api.covid19india.org/csv/latest/state_wise.csv'
#     return pd.read_csv(url)

# cnf = on_map()

# fig = px.choropleth(cnf, locations="IND",
#                     color="Confirmed", # lifeExp is a column of gapminder
#                     hover_name="Confirmed", # column to add to hover information
#                     color_continuous_scale=px.colors.sequential.Plasma)
    
# st.plotly_chart(fig)

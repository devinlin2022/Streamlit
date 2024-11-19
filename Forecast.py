import os
os.system("pip install streamlit")
os.system("pip install pandas")
os.system("pip install numpy")
os.system("pip install prophet")
os.system("pip install plotly")
os.system("pip install sklearn")
os.system("pip install xgboost")
os.system("pip install python-dateutil")
import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from dateutil.relativedelta import relativedelta

oildf = pd.read_html("https://www.indexmundi.com/commodities/?commodity=crude-oil-brent&months=360")[1]
coaldf = pd.read_html("https://www.indexmundi.com/commodities/?commodity=coal-australian&months=360")[1]
gasdf = pd.read_html("https://www.indexmundi.com/commodities/?commodity=natural-gas&months=360")[4]
sugardf = pd.read_html("https://www.indexmundi.com/commodities/?commodity=sugar&months=360")[4]
oredf = pd.read_html("https://www.indexmundi.com/commodities/?commodity=iron-ore&months=360")[1]
copperdf = pd.read_html("https://www.indexmundi.com/commodities/?commodity=copper&months=360")[4]
oildf.drop('Change', inplace = True, axis = 1)
coaldf.drop('Change', inplace = True, axis = 1)
gasdf.drop('Change', inplace = True, axis = 1)
sugardf.drop('Change', inplace = True, axis = 1)
oredf.drop('Change', inplace = True, axis = 1)
copperdf.drop('Change', inplace = True, axis = 1)
oildf.rename(columns = {'Price': 'oil_price'}, inplace = True)
coaldf.rename(columns = {'Price': 'coal_price'}, inplace = True)
gasdf.rename(columns = {'Price': 'gas_price'}, inplace = True)
sugardf.rename(columns = {'Price': 'sugar_price'}, inplace = True)
oredf.rename(columns = {'Price': 'ore_price'}, inplace = True)
copperdf.rename(columns = {'Price': 'copper_price'}, inplace = True)
df = (oildf.merge(coaldf).merge(gasdf).merge(sugardf).merge(oredf).merge(copperdf))
df.index = pd.to_datetime(df['Month'], format='%b %Y')
df.drop('Month', inplace = True, axis = 1)
odf = df.copy()

st.title('Commodity Price Forecast App')
commo = ('oil_price', 'coal_price', 'gas_price', 'sugar_price', 'ore_price', 'copper_price')
target = st.selectbox('Select item for forecast', commo)

data_load_state = st.text('Loading data...')
data = df[target]
data_load_state.text('Loading data... done!')

st.subheader('Raw data')
st.write(data)

# Plot raw data
def plot_raw_data():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df.index, y=df[target]))
	fig.layout.update(title_text='Historical Price Curve', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)

plot_raw_data()

n_months = st.slider('Number of months for prediction:', 1, 4)

# Predict forecast
forecast_out = n_months
df['Y'] = df[target].shift(-forecast_out)
X = np.array(df.drop(['Y'], 1))
X = preprocessing.scale(X)
X_lately = X[-forecast_out:]
X = X[:-forecast_out]
y = np.array(df['Y'])
y = y[:-forecast_out]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
clf = XGBRegressor(learning_rate = 0.1, max_depth = 3, n_estimators = 200, objective = 'reg:squarederror')
clf.fit(X_train, y_train)

forecast_set = clf.predict(X_lately)
df['Forecast'] = np.nan
for i in forecast_set:
    next_date = df.iloc[-1].name + relativedelta(months=1)
    df.loc[next_date] = [np.nan for _ in range(len(df.columns)-1)]+[i]

# Show and plot forecast
st.subheader('Forecast data')
st.write(df[df['Forecast'].notnull()]['Forecast'])

st.write(f'Forecast plot for {n_months} months')
def plot_forecast():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df.index, y=df[target]))
	fig.add_trace(go.Scatter(x=df.index, y=df['Forecast']))
	fig.layout.update(title_text='Forecast Graph', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)

plot_forecast()
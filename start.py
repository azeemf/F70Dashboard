from time import sleep
from xml.dom.minidom import CharacterData
import streamlit as st
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px 
import numpy as np
import pandas as pd
from datetime import datetime as dt

st.set_page_config(
        page_title="F70 Dashboard",
        page_icon="🌅",
        layout="wide",
    )

@st.cache
def convert_df(df):
   return df.to_csv().encode('utf-8')

st.title("F-70H Compressor Monitoring Dashboard")

with st.expander("Overview"):

    col1, col2 = st.columns(2)

    with col1:
        timeh = st.empty()

    with col2:
        st.text("Online ")
        oimg = st.empty()

with st.sidebar:

    scol1, scol2 = st.columns(2)

    with scol1:
        tempMetric = st.empty()
        avtempMetric = st.empty()
    with scol2:
        presMetric = st.empty()
        avgpresMetric = st.empty()

temp = pd.DataFrame({'Temp' : [np.random.randint(0, 100)], 'Time': [dt.now()]})
pres = pd.DataFrame({'Pres' : [np.random.randint(50, 500)], 'Time': [dt.now()]})

figcol1, figcol2 = st.columns(2)

with figcol1:
    tempFig = st.empty()
with figcol2:
    presFig = st.empty()

download_data = convert_df(pd.concat([temp, pres]))
st.download_button("Download Data", data=download_data, file_name="F70Data.csv")

bcol1, bcol2 = st.columns(2)

with bcol1:
    st.text("Designed and Developed by")
    st.image("MBA Creations Logo.png")

with bcol2:
    st.text("Partnered With")
    st.image("ucll.png")

# Start Of Loop

while 1:
    raw_temp_data = np.random.randint(0, 100)
    raw_pres_data = np.random.randint(50, 500)
    timeh.text(str(dt.now()))

    tempMetric.metric("Live Temp", raw_temp_data)
    avtempMetric.metric("Average Temp", temp.mean())

    presMetric.metric("Live Pressure", raw_pres_data)
    avgpresMetric.metric("Average Pressure", pres.mean())

    oimg.image('ocircle.png', width = 10)

    temp_in_data = pd.DataFrame({'Temp' : [raw_temp_data], 'Time': [dt.now()]})
    temp = pd.concat([temp, temp_in_data], ignore_index=True)

    pres_in_data = pd.DataFrame({'Pres' : [raw_pres_data], 'Time': [dt.now()]})
    pres = pd.concat([pres, pres_in_data], ignore_index=True)

    display_temp = temp.tail(10)
    display_pres = pres.tail(10)

    with tempFig.container():
        tfig = px.line(display_temp, 'Time', 'Temp', width=500, markers={'color' : 'red'})
        tfig.update_layout(yaxis_range=[0,100])
        st.write(tfig)
    with presFig.container():
        pfig = px.line(display_pres, 'Time', 'Pres', width=500, markers={'color' : 'blue'})
        pfig.update_layout(yaxis_range=[50,500])
        st.write(pfig)

    sleep(1)



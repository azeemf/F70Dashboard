from py_compile import PyCompileError
from time import sleep
import streamlit as st
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px 
import numpy as np
import pandas as pd
from datetime import datetime as dt
import serial
from helpers import rec_response
import os
import time

dataDirPath = 0
originalPath = os.getcwd()
prevDay = dt.now().day
pCOM = 0

st.set_page_config(
        page_title="F70 Dashboard",
        page_icon="📈",
        layout="wide",
    )

#find COM.numfile in dir and change number to the COM port associated with the compressor device

alertMessage = st.empty()

def findCOM():
    global inCom
    global pCOM
    comFile = open("COM.numfile", "r")
    inCom = "COM" + str(comFile.read())
    comFile.close()
    pCOM = inCom

findCOM()

print(str(dt.now()) + " --- " + pCOM + " Selected")

try:
    os.mkdirs("Data")
    newPath = os.path.join(os.getcwd(), "Data")
    os.chdir(newPath)
    dataDirPath = newPath
    prevDay = dt.now().day
except:
    print(str(dt.now()))
    dataDirPath = os.path.join(os.getcwd(), "Data")

def CheckSerial():
    helcomp_serial_port = inCom
    ser=serial.Serial()
    ser.port=helcomp_serial_port
    ser.baudrate=9600
    ser.bytesize=serial.EIGHTBITS
    ser.parity=serial.PARITY_NONE
    ser.stopbits=1
    ser.timeout=5
    ser.xonxoff=0
    try:
        ser.open()
        ser.close()
        return True
    except:
        st.error("⛔ Serial Port Could Not Be Opened - Please Rerun")
        return False

def Read(pCom):

    helcomp_serial_port = pCom # may need to change, if serial port number changes
    path = os.path.dirname(os.path.abspath(__file__)) # relative directory path

    # Create an instance of serial object, set serial parameters for Sumitomo F70L Helium Compressor
    ser=serial.Serial()
    ser.port=helcomp_serial_port
    ser.baudrate=9600
    ser.bytesize=serial.EIGHTBITS
    ser.parity=serial.PARITY_NONE
    ser.stopbits=1
    ser.timeout=5
    ser.xonxoff=0

    # read data
    ser.open()
    # temperatures
    sendstring = b"$TEAA4B9\r"
    ser.flushInput()
    ser.flushOutput()
    ser.write(sendstring)
    temperatures = rec_response(ser)
    time.sleep(0.05) # pause to ensure readiness
    print(str(dt.now()) + " --- " + str(temperatures))
    temperatures = str(temperatures)
    retList = [temperatures]

    # pressures 
    sendstring = b"$PRA95F7\r"
    ser.flushInput()
    ser.flushOutput()
    ser.write(sendstring)
    pressures = rec_response(ser)
    time.sleep(0.05) # pause to ensure readiness
    print(str(dt.now()) + " --- " + str(pressures))
    pressures = str(pressures)
    retList.append(pressures)

    # status 
    sendstring = b"$STA3504\r"
    ser.flushInput()
    ser.flushOutput()
    ser.write(sendstring)
    status = rec_response(ser)
    time.sleep(0.05) # pause to ensure readiness
    ser.close()

    # interpret status bytes
    print(str(dt.now()) + " --- " + str(status))

    retList.append(status)

    return retList

@st.cache
def convert_df(df):
   return df.to_csv().encode('utf-8')

os.chdir(str(originalPath)) 

st.title("F-70H Compressor Monitoring Dashboard")
status = st.empty()
status.write("Waiting...")

with st.expander("Overview"):

    col1, col2 = st.columns(2)

    with col1:
        timeh = st.empty()

    with col2:
        oText = st.empty()    
        if CheckSerial() == True:
            oText = st.write("Online - " + inCom + ": 🟢")

            #serData = Read()

            HelDis = 54
            WOut = 50
            WIn = 21
            pSig = 100

            dfHelDis = pd.DataFrame({'HelDis' : [HelDis], 'Time': [dt.now()]})
            dfWIn = pd.DataFrame({'WIn' : [WIn], 'Time': [dt.now()]})
            dfWOut = pd.DataFrame({'WOut' : [WOut], 'Time': [dt.now()]})
            pres = pd.DataFrame({'pSig' : [pSig], 'Time': [dt.now()]})

        else:
            oText = st.write("Online - " + inCom + ": 🔴")
            st.experimental_rerun()

with st.sidebar:

    scol1, scol2 = st.columns(2)

    with scol1:
        HelDisMetric = st.empty()
        avHelDisMetric = st.empty()
        WIMetric = st.empty()
        avWIMetric = st.empty()
    with scol2:
        presMetric = st.empty()
        avgpresMetric = st.empty()
        WOMetric = st.empty()
        avWOMetric = st.empty()

    timeSelect = st.selectbox("Select time between data acquistion cycles", ('Realtime', '1 min', '10 min', '1 hour'))    
    
    st.write("NOTE - Please do not use compressor state switch as off yet...")
    onoff = st.select_slider('Select Compressor State', options=['On', 'Off'])
    ooButton = st.button(label="Execute")
    

figcol1, figcol2 = st.columns(2)

with figcol1:
    tempFig = st.empty()
    WIFig = st.empty()
with figcol2:
    presFig = st.empty()
    WOFig = st.empty()

st.text(" ")
st.text(" ")
st.text(" ")

downloadButton = st.empty()

st.text(" ")
st.text(" ")
st.text(" ")

bcol1, bcol2 = st.columns(2)

with bcol1:
    st.text("Designed and Developed by")
    st.image("MBA Creations Logo.png")

with bcol2:
    st.text("Partnered With")
    st.image("ucll.png")

sWarning = st.empty()

def updateMetrics():
    HelDisMetric.metric("Live Helium Discharge Temp", value = str(HelDis) + " °C", delta=HelDis - prevHelDis)
    avHelDisMetric.metric("Average Helium Discharge Temp", dfHelDis['HelDis'].mean())

    WOMetric.metric("Live Water Out Temp", value = str(WOut) + " °C", delta=WOut - prevWOut)
    avWOMetric.metric("Average Water Out Temp", dfWOut['WOut'].mean())

    WIMetric.metric("Live Water In Temp", value = str(WIn) + " °C", delta=WIn - prevWIn)
    avWIMetric.metric("Average Water In Temp", dfWIn['WIn'].mean())

    presMetric.metric("Live Pressure", value = str(pSig) + " PSI", delta=pSig - prevpSig)
    avgpresMetric.metric("Average Pressure", pres['pSig'].mean())

def updatePd():

    global dfHelDis
    global dfWIn
    global dfWOut
    global pres

    temp_in_data = pd.DataFrame({'HelDis' : [HelDis], 'Time': [dt.now()]})
    dfHelDis = pd.concat([dfHelDis, temp_in_data], ignore_index=True)

    temp_in_data = pd.DataFrame({'WIn' : [WIn], 'Time': [dt.now()]})
    dfWIn = pd.concat([dfWIn, temp_in_data], ignore_index=True)

    temp_in_data = pd.DataFrame({'WOut' : [WOut], 'Time': [dt.now()]})
    dfWOut = pd.concat([dfWOut, temp_in_data], ignore_index=True)

    pres_in_data = pd.DataFrame({'pSig' : [pSig], 'Time': [dt.now()]})
    pres = pd.concat([pres, pres_in_data], ignore_index=True)

def updateFigs():
    with tempFig.container():
        tfig = px.line(display_HelDis, 'Time', 'HelDis', width=500, title="Helium Discharge Temp")
        st.write(tfig)
    with presFig.container():
        pfig = px.line(display_pres, 'Time', 'pSig', width=500, title="pSig Pressure")
        st.write(pfig)
    with WOFig.container():
        tfig = px.line(display_WO, 'Time', 'WOut', width=500, title="Water Out Temp")
        st.write(tfig)
    with WIFig.container():
        tfig = px.line(display_WI, 'Time', 'WIn', width=500, title="Water In Temp")
        st.write(tfig)

def getSleepTime():
    if timeSelect == 'Realtime':
        return 0.01
    elif timeSelect == '1 min':
        return 60
    elif timeSelect == '10 min':
        return 600
    elif timeSelect == '1 hour':
        return 3600    

def dayCheck(pD):
    global dataDirPath
    if pD != dt.now().day:
        print(str(dt.now()) + " --- New Day")
        newDay(dataDirPath)
    else:
        pass

def newDay(ddp):

    os.chdir(str(ddp))
    
    try:
       # os.mkdirs(dt.now())
        os.mkdirs(dt.now().strftime('%Y%m%d'))
        print("dir made")
    except:
        pass
    os.chdir(dt.now().strftime('%Y%m%d'))

def saveData():
    pass

def shutdownSeq():
    while 1:
        print("SHUTDOWN")
        sleep(1)

def checkOOStatus(oo):
    if onoff == 'Off':
        shutdownSeq()
    else:
        pass

# Start Of Loop

newDay(dataDirPath)

while 1:

    checkOOStatus(onoff)

    status.write("Ready")

    os.chdir(originalPath)

    prevHelDis = HelDis
    prevWOut = WOut
    prevWIn = WIn
    prevpSig = pSig
    prevDay = dt.now().day

    serData = Read(pCOM)
    sWarning = st.empty()
    HelDis = int(serData[0][7:10])
    WOut = int(serData[0][11:14])
    WIn = int(serData[0][15:18])
    pSig = int(serData[1][7:10])

    timeh.text(str(dt.now()))

    updateMetrics()

    updatePd()

    display_HelDis = dfHelDis.tail(10)
    display_WO = dfWOut.tail(10)
    display_WI = dfWIn.tail(10)
    display_pres = pres.tail(10)

    updateFigs()

    dfHelDis.to_csv(index=False)
    dfWIn.to_csv(index=False)
    dfWOut.to_csv(index=False)
    pres.to_csv(index=False)

    dayCheck(prevDay)

    sL = getSleepTime()
    
    try:
        status.write("Waiting for " + str(sL) + " secs")
        sleep(sL)
    except KeyboardInterrupt:
        sL = getSleepTime()
        print(str(dt.now()) + " --- " + "Cycle wait interrupted. New cycle time - " + str(sL) + " seconds")

    #download_data = convert_df(pd.concat([temp, pres], ignore_index=True))
    #with downloadButton:
    #   st.download_button("Download Data", data=download_data, file_name="F70Data.csv")

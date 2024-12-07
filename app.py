from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle as pkl
import requests
import os
from dotenv import load_dotenv, dotenv_values 
#load in the model
with open('weather_model.pkl','rb') as f:
    model= pkl.load(f)

load_dotenv()
print(type(os.getenv("default")))
#fetch geo coding api
def geocode(city):
  base_link = "http://api.openweathermap.org/geo/1.0/direct?q="
  api_key = os.getenv("default")
  link = f'{base_link}{city}&limit=2&appid={api_key}'
  response = requests.get(link)
  data = response.json()
  return data

def weatherCalls(lat, lon):
  key = os.getenv("test")
  link = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric'
  response = requests.get(link)
  data = response.json()
  return data['main']['temp'], data['main']['humidity'], data['wind']['speed'],data['clouds']['all'],data['main']['pressure']

app = Flask(__name__)

@app.route('/', methods= ["GET","POST"])
def weatherHome():
    if request.method == "POST":
       string = request.form['city']
       d_json = geocode(string)
       if(len(d_json) > 0):
          lon = d_json[0]['lon']
          lat = d_json[0]['lat']
          temp, hum, w_speed, cloud, press = weatherCalls(lat, lon)
          conditions = np.array([[temp,hum,w_speed,cloud,press]])
          res = model.predict(conditions)
          if(res[0] == 1):
            result = "there will be rain"
          else: 
             result = "no rain"
          
          return render_template('result.html', searchcity = result)
       else:
          wrong = "sorry something went wrong"
          print(wrong)
          return render_template('err.html', warn = wrong)

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug = True) 
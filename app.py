#!/usr/bin/env python
from datetime import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)

import sqlite3

date_1 = ''
date_2 = ''
# Retrieve LAST data from database

def getLastData():
	'''gets the last sensor values'''
	con=sqlite3.connect('../../mqtt2dbIOT/databasepi')
	cur=con.cursor()
	data = cur.execute("SELECT rpi_datetime, temperature, humidity, pressure FROM data ORDER BY ID DESC LIMIT 1").fetchone()
	con.close()
	return data

def get_data_samples(samples=100, date1='', date2=''):
	'''gets the data between 2 dates or a specified amount'''
	con=sqlite3.connect('../../mqtt2dbIOT/databasepi')
	cur=con.cursor()
	if date1 != '' and date2 != '':
		sql_statement = f"SELECT rpi_datetime, temperature, humidity, pressure FROM data WHERE rpi_datetime BETWEEN '{date1}' AND '{date2}';"
		print(sql_statement)
		data = cur.execute(sql_statement).fetchall()
	else:
		data = cur.execute(f"SELECT rpi_datetime, temperature, humidity, pressure FROM data ORDER BY ID DESC LIMIT {samples}").fetchall()
	
	date = []
	temp = []
	humidity = []
	pressure = []
	for data_point in data:
		date.append(datetime.fromisoformat(data_point[0]))
		temp.append(data_point[1])
		humidity.append(data_point[2])
		pressure.append(data_point[3])
	con.close()
	return date, temp, humidity, pressure		


# main route 
@app.route("/")
def index():
	'''main page with the data'''
	time, temp, hum, pressure = getLastData()
	templateData = {
	  'time'		: time,
      'temp'		: temp,
      'hum'			: hum,
	  'pressure'	: pressure
	}
	return render_template('index.html', **templateData)


@app.route('/', methods=['POST'])
def my_form_post():
	'''POST method to get the between dates'''
	global date_1
	global date_2
	date_1 = request.form["date1"]
	date_2 = request.form["date2"]
	time, temp, hum, pressure = getLastData()
    
	templateData = {
	  'time'		: time,
      'temp'		: temp,
      'hum'			: hum,
	  'pressure'	: pressure
	}
	return render_template('index.html', **templateData)
	
@app.route('/plot/temp')
def plot_temp():
	'''Plots the temperature'''
	time, temps, hums, pressure = get_data_samples(date1=date_1, date2=date_2)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Temperature [°C]")
	axis.set_xlabel("Date")
	axis.grid(True)
	xs = time
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/hum')
def plot_hum():
	'''plots the humidity'''
	time, temps, hums, pressure = get_data_samples(date1=date_1, date2=date_2)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity [%]")
	axis.set_xlabel("Date")
	axis.grid(True)
	xs = time
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/pressure')
def plot_pressure():
	'''plots the pressure'''
	time, temps, hums, pressure = get_data_samples(date1=date_1, date2=date_2)
	ys = pressure
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Pressure [Pascals]")
	axis.set_xlabel("Date")
	axis.grid(True)
	xs = time
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=2000, debug=False)


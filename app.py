# import packages
from flask import Flask, render_template, request, redirect
import requests
import numpy as np
import pandas as pd
import bokeh
import datetime
from bokeh.models import Range1d
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.embed import components
bv = bokeh.__version__

# start coding
app = Flask(__name__)
app.vars={}
#feat = ['Open','Close','Range']

# initial page
@app.route('/')
def main():
	return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
	# direct to the first page
	# collect stock name, start year, month and time span
	if request.method == 'GET':
		return render_template('index.html')
	else:
		#request was a POST
		app.vars['ticker'] = request.form['ticker'].upper()
		app.vars['start_year'] = request.form['year']
		app.vars['start_month'] = request.form['month']
		app.vars['timespan'] = request.form['timespan']
		app.vars['desc']= '%s Price' % app.vars['ticker']
		try: 
			int(app.vars['start_year'])
			app.vars['tag_year'] = 'Start year specified as year %s' % app.vars['start_year']
			int(app.vars['start_month'])
			app.vars['tag_month'] = 'Start month specified as month %s' % app.vars['start_month']
			int(app.vars['timespan'])
			app.vars['tag_span'] = 'Time span specified as %s month' % app.vars['timespan']
		except ValueError: 
			app.vars['start_year'] = ''
			app.vars['tag_year'] = 'Start year not specified/recognized'
			app.vars['start_month'] = ''
			app.vars['tag_month'] = 'Start month not specified/recognized'
			app.vars['timespan'] = ''
			app.vars['tag_span'] = 'Time span not specified/recognized'
		#app.vars['select'] = [feat[q] for q in range(3) if feat[q] in request.form.values()]
		return redirect('/graph')

# get data
@app.route("/data")
def data():
  # get stock data
	req = 'https://www.quandl.com/api/v3/datasets/WIKI/'
	req = '%s%s.json?&collapse=weekly' % (req,app.vars['ticker'])
	if app.vars['start_year']!='':
		req = '%s&start_date=%s-01-01' % (req,app.vars['start_year'])
	r = requests.get(req)	
	cols = r.json()['dataset']['column_names'][0:5]
	df = pd.DataFrame(np.array(r.json()['dataset']['data'])[:,0:5],columns=cols)
	df.Date = pd.to_datetime(df.Date)
	df[['Open','High','Low','Close']] = df[['Open','High','Low','Close']].astype(float) 
	df.columns=['date','Open','High','Low','Close'];
	if app.vars['start_year']!='':
		if df.date.iloc[-1].year>int(app.vars['start_year']):
			app.vars['tag_year'] = '%s, but Quandl record begins in %s' % (app.vars['tag_year'],df.date.iloc[-1].year)
	#app.vars['desc'] = r.json()['dataset']['name'].split(',')[0]  
	return df.to_csv(index=False,sep="\t")

@app.route('/graph',methods=['GET','POST'])
def graph():
	'''
	# transfer json data to date frame
	start_date=datetime.date(year=int(app.vars['start_year']),day=1,month=int(app.vars['start_month']));
	end_date=datetime.date(year=int(app.vars['start_year'])+int(app.vars['timespan']),day=1,month=int(app.vars['start_month']));

  # plots
	p = figure(plot_width=450, plot_height=450, title=app.vars['ticker'], x_axis_type="datetime",x_range=Range1d(start_date,end_date))
	if 'Range' in app.vars['select']:
		tmpx = np.array([df.Date,df.Date[::-1]]).flatten()
		tmpy = np.array([df.High,df.Low[::-1]]).flatten()
		p.patch(tmpx, tmpy, alpha=0.3, color="gray",legend='Range (High/Low)')
	if 'Open' in app.vars['select']:
		p.line(df.Date, df.Open, line_width=2,legend='Opening price')
	if 'Close' in app.vars['select']:
		p.line(df.Date, df.Close, line_width=2, line_color="red",legend='Closing price')
		
	# axis labels
	p.xaxis.axis_label = "Date"
	p.xaxis.axis_label_text_font_style = 'bold'
	p.xaxis.axis_label_text_font_size = '16pt'
	p.xaxis.major_label_orientation = np.pi/4
	p.xaxis.major_label_text_font_size = '14pt'
	p.yaxis.axis_label = "Stock price ($)"
	p.yaxis.axis_label_text_font_style = 'bold'
	p.yaxis.axis_label_text_font_size = '16pt'
	p.yaxis.major_label_text_font_size = '14pt'	
	script, div = components(p)
	'''
	return render_template('graph.html', ticker=app.vars['ticker'],
							ttag=app.vars['desc'], yrtag=app.vars['tag_year'])
		
	
@app.errorhandler(500)
def error_handler(e):
	return render_template('error.html',ticker=app.vars['ticker'],year=app.vars['start_year'])

    
# # If main
# -----------------------------------------------------|
if __name__ == '__main__':
  app.run(port=50000,debug=True)
  
  
  
#                                    END ALL
# # ---------------------------------------------------------------------------|
    

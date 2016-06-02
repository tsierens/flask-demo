from flask import Flask, render_template, request, redirect
import requests
import simplejson
import os
import re
import pandas as pd
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.palettes import Spectral4

app = Flask(__name__)
app.options = ["Open", "Adj_Open", "Close","Adj_Close"]
app.names = ["Open", "Adj. Open", "Close", "Adj. Close"]
app.div=[]
app.script = ''

url = "https://www.quandl.com/api/v3/datasets/WIKI/"
ftype = ".csv"
apikey = os.environ["APIKEY"]

def split_string(tickers):
    sep = re.compile(r"\W+")
    querys = re.split(sep, tickers.strip())
    querys = [val.upper() for val in querys]
    return querys

def get_data(queries, selection):
    data = {}
    for query in queries:
        response = requests.get(url+query+ftype,apikey)
        if response.ok:
            data[query] = pd.read_csv(response.url,index_col='Date', usecols = selection)[::-1]
            data[query].index = pd.to_datetime(data[query].index)
        else:
            data[query] = None
    return data

def make_plots(data):
    figs = []
    tools = 'pan,wheel_zoom,box_zoom,reset,save'
    colours = Spectral4[:]
    for ticker, plot_data in data.iteritems():
        fig = figure(title = ticker, y_axis_label = "Price (USD)", 
                     x_axis_type = "datetime", tools = tools, width = 800, height = 400)
        for i, name in enumerate(plot_data.columns):
            fig.line(plot_data.index, plot_data[name], color = colours[i],legend = name, line_width = 2, line_alpha = 0.85)
        
        fig.legend.location = "top_left"
        
        fig.xgrid.grid_line_width = 2
        fig.ygrid.grid_line_width = 2
        fig.xgrid.grid_line_color = 'white'
        fig.ygrid.grid_line_color = 'white'
        figs.append(fig)
    return figs


@app.route('/')
def main():
  return redirect('/index')

@app.route('/reset', methods = ['GET'])
def reset():
	return redirect('/index')

@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html',op=app.options, names = app.names, script = "", div = simplejson.dumps(
                []),failed = simplejson.dumps([]))
    if request.method == 'POST':
        options = [word for word in app.names if request.form.get(word) is not None]
        options.insert(0,'Date')
        tickers = request.form.get('ticker')
        tickers = split_string(tickers)
        data = get_data(tickers,options)
        failed = []
        dummy_data = dict(data)
        for key in data:
            if data[key] is None:
                failed.append(key)
                del dummy_data[key]
        data = dict(dummy_data)
        failed_text = ''
        if failed:
            failed_text = 'The following are not valid ticker ids: '
            for item in failed:
                failed_text = failed_text + item + ', '
            failed_text = failed_text[:-2]
        
        plots = make_plots(data)
        
        app.script, app.div = components(plots)
        
        print app.div
        return render_template('index.html',op = app.options, names = app.names, script = app.script, div = simplejson.dumps(
                app.div), failed = simplejson.dumps(failed_text))

if __name__ == '__main__':
  port = int(os.environ.get("PORT",5000))
  app.run(debug=False, host='0.0.0.0', port=port)

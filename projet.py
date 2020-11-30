from flask import Flask, redirect, url_for, render_template, request
from elasticsearch import Elasticsearch

from io import StringIO
import base64
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import pandas as pd
import seaborn as sns

app = Flask(__name__)
es = Elasticsearch()

def plotFig(data,x,y,siz):
    img = io.BytesIO()
    fig = plt.figure( figsize=(10,10))
    plotdata = sns.scatterplot(data=data[:siz],x=x,  y=y)
    plotdata.set_xticklabels(data[:siz][x],rotation=90)
    plt.tight_layout()
    fig.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url


@app.route("/shakespear", methods=["POST","GET"])
def shakespear():
    """
    Flask page to query text entry 
    """
    q = request.form.get("search_me")
    sor = "_score"
    res = "Welcome"
    count = ""
    sor_l = ["_score","speaker",'play_name','speech_number']
    siz = 10
    if request.method == "POST":
        if request.form.get("size_") is not None and request.form.get("size_") != "Size" and request.form.get("size_") != "":
            siz = int(request.form.get("size_"))
        if request.form.get("sort_by") is not None and request.form.get("sort_by") != "Sort by":    
            sor = request.form.get("sort_by")
        order = request.form.get("order_by")
        if order is not None and order!="Sort Order" :
            sor = sor + ":" + order
        query = {"query":  {
                            "match": {
                                    "text_entry.english": {
                                    "query": q
                                            }
                                    }
                        }
            }
    # send qeury request to elastic
    if q is not None:
        res = es.search(
            index="shakespeare-catalog-2",
            body=query,
            sort=sor,
            size=siz)
        count = res["hits"]["total"]["value"]
        res= res["hits"]["hits"]
    return render_template("shakespear.html",cont=res,coun=count,sor_l=sor_l)


@app.route("/flight", methods=["POST","GET"])
def flight():
    """
    Search Flights by Origin
    """
    sor="_score"
    res="Welcome"
    count=""
    source=""
    sor_l = ["AvgTicketPrice","DistanceMiles",'FlightTimeHour','timestamp']
    siz = 10
    if request.method == "POST":
        if request.form.get("size_") is not None and request.form.get("size_")!="Size" and request.form.get("size_")!="":
            siz = int(request.form.get("size_"))
        if request.form.get("source") is not None and request.form.get("source")!="source" and request.form.get("source")!="":
            source = request.form.get("source")
            source = source.capitalize()
        if request.form.get("sort_by") is not None and request.form.get("sort_by")!="Sort by":
            sor = request.form.get("sort_by")
        order = request.form.get("order_by")
        if order is not None and order != "Sort Order":
            sor = sor + ":" + order
    # define query
    query = {
            "query": {
                "query_string": {
                    "fields": ["Origin"],
                    "query": "*"+source+"*"
                }
                }
            }
    # send request to ES
    if  source is not None and source!="":
        res = es.search(index="kibana_sample_data_flights",body = query,sort=sor,size=siz)
        count = res["hits"]["total"]["value"]
        res= res["hits"]["hits"]
    return render_template("flight.html",cont=res,coun=count,sor_l=sor_l,to_plot=False)


@app.route("/flight_dest", methods=["POST","GET"])
def flight_dest():
    """
    Search Flights by Destination
    """
    sor="_score"
    res="Welcome"
    count=""
    dest = ""
    sor_l = ["AvgTicketPrice","DistanceMiles",'FlightTimeHour','timestamp']
    siz = 10
    if request.method == "POST":
        if request.form.get("size_") is not None and request.form.get("size_")!="Size" and request.form.get("size_")!="":
            siz = int(request.form.get("size_"))
        if request.form.get("source") is not None and request.form.get("source")!="source" and request.form.get("source")!="":
            dest = request.form.get("source")
            dest = dest.capitalize()
        
        if request.form.get("sort_by") is not None and request.form.get("sort_by")!="Sort by":
            sor = request.form.get("sort_by")
        order = request.form.get("order_by")
        if order is not None and order != "Sort Order":
            sor = sor + ":" + order
        
    query = {
            "query": {
                "query_string": {
                    "fields": ["Dest"],
                    "query": "*"+dest+"*"
                }
                }
            }
    
    if dest is not None and dest != "":
        res = es.search(index="kibana_sample_data_flights",body = query,sort=sor,size=siz)
        count = res["hits"]["total"]["value"]
        res= res["hits"]["hits"]
    return render_template("flight.html",cont=res,coun=count,sor_l=sor_l,to_plot=False)

@app.route("/shakespear/visualization", methods=["POST","GET"])
def shake():
    data = pd.read_csv("./data/shakespear.csv")
    siz = 100
    x_ax = "play_name"
    y_ax = "speaker"
    if request.method == "POST":
        if request.form.get("size_plt") is not None and request.form.get("size_plt") != "Size" and request.form.get("size_plt") != "":
            siz = int(request.form.get("size_plt"))
        if request.form.get("x_ax") is not None and request.form.get("x_ax")!="X axis" and request.form.get("x_ax")!="":
            x_ax = request.form.get("x_ax")
        if request.form.get("y_ax") is not None and request.form.get("y_ax")!="Y axis" and request.form.get("y_ax")!="":
            y_ax = request.form.get("y_ax")
            
    fig = plotFig(data, x_ax, y_ax, siz)
    return render_template("shakespear.html",plot_graph=fig,to_plot=True,sor_l=data.columns.tolist())

@app.route("/flight/visualization",methods = ["POST","GET"])
def fli():
    data = pd.read_csv("./data/flight.csv")
    siz = 100
    x_ax = "Dest"
    y_ax = "Origin"
    if request.method == "POST":
        if request.form.get("size_plt") is not None and request.form.get("size_plt")!="Size" and request.form.get("size_plt")!="":
            siz = int(request.form.get("size_plt"))
        if request.form.get("x_ax") is not None and request.form.get("x_ax")!="X axis" and request.form.get("x_ax")!="":
            x_ax = request.form.get("x_ax")
        if request.form.get("y_ax") is not None and request.form.get("y_ax")!="Y axis" and request.form.get("y_ax")!="":
            y_ax = request.form.get("y_ax")
            
    fig = plotFig(data,x_ax,y_ax,siz)
    return render_template("flight.html",plot_graph=fig,to_plot=True,sor_l=data.columns.tolist())

@app.route("/home",methods = ["POST","GET"])
def home():
    return render_template("home.html")


if __name__=="__main__":
    app.run(port = 8000)
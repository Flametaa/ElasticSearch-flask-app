from flask import Flask, redirect, url_for, render_template, request
from elasticsearch import Elasticsearch
app = Flask(__name__)
es = Elasticsearch()


@app.route("/shakespear",methods = ["POST","GET"])
def shakespear():
    q = request.form.get("search_me")
    res="Welcome"
    coun=""
    print(q)
    query = {"query":  {
                            "match": {
                                    "text_entry": {
                                    "query": q
                                            }
                                    }
                        }
            }
    if q is not None:
        res = es.search(index="shakespeare-catalog-2",body = query)
        coun = res["hits"]["total"]["value"]
        res= res["hits"]["hits"]
    return render_template("index.html",cont=res,coun=coun)


@app.route("/flight",methods = ["POST","GET"])
def flight():
    q = request.form.get("search_me")
    res="Welcome"
    coun=""
    print(q)
    query = {"query":  {
                            "match": {
                                    "text_entry": {
                                    "query": q
                                            }
                                    }
                        }
            }
    if q is not None:
        res = es.search(index="kibana_sample_data_flights",body = query)
        coun = res["hits"]["total"]["value"]
        res= res["hits"]["hits"]
    return render_template("index.html",cont=res,coun=coun)




if __name__=="__main__":
    app.run(port = 8000)
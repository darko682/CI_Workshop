import cv2
import sys
import flask
import pandas as pd
import jsonpickle
import numpy as np
from flask import Flask, request, Response
import time
import json
import requests

app = flask.Flask(__name__)

# To send healthy status to SageMaker
# Creation of the ping.html page
@app.route('/', methods=['GET'])
def home():
    return ("<center><h1><b> Pruebas</b></h1></center>")

@app.route('/ping', methods=['GET'])
def ping():
    status = 200 #if health else 404
    return flask.Response(response='\n', status=status, mimetype='application/json')

@app.route('/cachar', methods=['GET', 'POST'])
def cachar():
    
    #geting values from database
    data_source = pd.read_csv('./prueba.csv',header=[1])    
    
    # Distance Caculator for preocessing data
    def dist(PL_Values, d_2_process, n_col):
        distance=0
        for i in range(0, n_col):
            distance += (PL_Values[i]-d_2_process[i])**2
        distance = np.sqrt(distance)
        return distance
        
        
    cola = request.data
    values12 = cola.decode()
    python_dict = json.loads(cola)
    
    
    #print(python_dict.get("tags","none"))
    client_requirements_tags = python_dict.get("tags","none")
    dataValues = python_dict.get("Experiencia","none")
    MountPeople = list(map(int,python_dict.get("gente","none")))
    print(MountPeople)
    
    client_requirements_PL_values = list(map(int,dataValues))
    
    
    
    # Centroids definitions
    accentures_standard_PL_values=[1] * len(dataValues)
    none_PL_values=[0] * len(dataValues)
    not_sure_PL_values=[1] * len(dataValues)
    low_PL_values=[2] * len(dataValues)
    moderate_PL_values=accentures_standard_PL_values
    high_PL_values=[4] * len(dataValues)
    
    # Number of clusters
    k = 7

    # Pruning data
    data_to_explore = data_source[client_requirements_tags]

    # Knowledge Discovery
    client_distances = []
    accentures_distances = []
    data_to_process = data_to_explore
    CandidateReport = data_to_process
    data_to_process = data_to_process.drop(columns='Name')

    for row in range(0,data_to_process.shape[0]):
    # Use one line of the pandas data frame each time
        data2process = data_to_process[row: row + 1].values
        data2process = data2process.ravel()
        client_distances.append(dist(client_requirements_PL_values, data2process, data_to_process.shape[1]))
        accentures_distances.append(dist(accentures_standard_PL_values, data2process, data_to_process.shape[1]))


    CandidateReport.insert(data_to_explore.shape[1], 'ClientMatch',client_distances)
    CandidateReport.insert(data_to_explore.shape[1], 'AccentureMatch',accentures_distances)
    # Free memory
    del data_to_process,data2process
    CandidateReport.to_csv('CandidateReport.csv', sep=',', encoding='utf-8',index=False)
    
    #JsonConverter
    dataset1 = pd.read_csv('./CandidateReport.csv')
    dataset = dataset1.sort_values(by=["ClientMatch"], ascending=True)
    Y = dataset.iloc[ 0:MountPeople[0] :, 0:9].values
    client_requirements_tags.append("ClientMatch")
    client_requirements_tags.append("AccentureMatch")
    Z = client_requirements_tags
    
    start = time.time()
    things = {}
    things.update({'data' : []})

    for inc in range(len(Y)):
        todo = {}
        for dec in range(0,9):
            todo[Z[dec]] = Y[inc][dec]
        things['data'].append(todo)
    end = time.time()
    print(end - start)

        
    
    return (json.dumps(things, indent=4))


app.run(host='127.0.0.1', port=8080)

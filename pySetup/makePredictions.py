import json
import os
import os.path as path
import sys
import csv
import time
import joblib
import numpy as np
import logging

from sendMessages import printParent
from sendMessages import messageParent
from sendMessages import obviousPrint

logging.basicConfig()

fileNames = json.loads(sys.argv[4])
classifierName = sys.argv[5]
argv = json.loads(sys.argv[3])

if( classifierName[0:4] == 'clnn' ):
    nn = True
    X_file_name = fileNames['X_test_nn']
else:
    X_file_name = fileNames['X_test']

id_file_name = fileNames['id_test']

X = []
idColumn = []

# load up the prediction data set, without the header row
with open(X_file_name, 'rU') as x_file:
    inputRows = csv.reader(x_file)
    headerRow = False
    for row in inputRows:
        if(headerRow):
            X.append(row)
        else:
            headerRow = True


with open(id_file_name, 'rU') as id_file:
    inputRows = csv.reader(id_file)
    for row in inputRows:
        # the csv reader will read each row in as a list, even if that list only has a single item in it
        # append each row ID value to idColumn
        idColumn.append(row[0])

# load up the previously trained (and tuned!) classifier
classifier = joblib.load('pySetup/bestClassifiers/best' + classifierName + '/best' + classifierName + '.pkl')

if nn:
    X = np.array(X)

# get predictions for each item in the prediction data set
predictedResults = classifier.predict_proba(X)

if not os.path.exists('predictions'):
    os.makedirs('predictions')

with open( path.join( 'predictions', classifierName + argv['dataFile']) , 'w+') as predictionsFile:
    csvwriter = csv.writer(predictionsFile)

    # we are going to have to modify this when we allow it to make categorical predictions too. 
    # TODO: get the actual id and output column names
    csvwriter.writerow(['ID','Output'])
    for idx, prediction in enumerate(predictedResults):
        rowID = idColumn[idx]
        # I'm not sure why we're checking if prediction is already a list
            # or why we're taking the second item in that list
        try:
            len(prediction)
            csvwriter.writerow([rowID,prediction[1]])
        except:
            csvwriter.writerow([rowID,prediction])


# Nope. Each classifier writes it's own predictions to it's own file. 
    # we will keep an array in ppLib.js that has references to all the file names
    # the files will all be in a predictions folder, that will hold nothing but these files holding the predictions from a single classifier
    # once we have all of them written (this way we don't need to worry about asynchronicity issues, or multiple classifiers trying to write to the same file), we can go through and either centralize all of them into a single file, or just iterate through all of the files. 
    # if we can keep metadata on each file (or, in the array with the file names, hold objects that have information such as observed error rate, relative ranking within all the classifiers of that type, type of classifier, training time, etc.)




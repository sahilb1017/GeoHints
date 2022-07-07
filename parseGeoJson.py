import json
import geopandas as gpd
import pandas as pd
from pandas import DataFrame as df
import numpy as np
import glob
from decimal import *




#START OF DEF
def getCoordinates(frame):
    coordinatesLineString = frame["geometry"]
    toString = str(coordinatesLineString[0])
    toString = toString.replace("LINESTRING (", "")
    toString = toString.replace(")", "")
    coordinatesAsString = toString.split(", ")
    for i in range(0, len(coordinatesAsString)):
        coordinatesAsString[i] = coordinatesAsString[i].split(" ")
        coordinatesAsString[i].reverse()
        #At this point, coordiantesAsString should be a 2D array with each entry containg a set 
        #of ordered lat/long pairs
    
    return coordinatesAsString
#END OF DEF


#START OF DEF
def getTimeStampsAndDistance(frame):
    #timestamp extraction
    segments = frame['segments']
    asString = str(segments[0])
    asString = asString.split(', "steps"')
    asString = asString[1].replace(": [ ", "", 1)
    asString = asString.split("{")
    asString.pop(0)
    asString.pop(-1)

    waypoints = getWayPoints(asString)
    times, distances = calculateTimeDistance(waypoints)
    return times, distances
#END OF DEF


#START OF DEF
def getWayPoints(asString):
    waypoints = []
    for i in range(len(asString)):
        curr = asString[i].split('"')
        temp = []
        temp.append(curr[4])
        temp.append(curr[2])
        temp.append(curr[-1])
        temp[0] = temp[0].replace(": ", "")
        temp[0] = temp[0].replace(", ", "")
        temp[0] = Decimal(temp[0])
        temp[1] = temp[1].replace(": ", "")
        temp[1] = temp[1].replace(", ", "")
        temp[1] = Decimal(temp[1])
        temp[2] = temp[2].replace(": ", "")
        temp[2] = temp[2].replace(" }, ", "")
        temp[2] = json.loads(temp[2])
        waypoints.append(temp)
    return waypoints

#END OF DEF

#START OF DEF
def calculateTimeDistance(waypoints):
    times, distances = [0], [0]
    t, d = 0, 0

    for j in range(len(waypoints)):
        duration = waypoints[j][0]
        currDistance = waypoints[j][1] / 1000
        points = waypoints[j][2]
        num = points[1] - points[0]
        interval = duration / num
        interval2 = currDistance / num
        t = times[-1]
        d = distances[-1]

        for k in range(num):
            t = t + interval
            d = d + interval2
            times.append(t)
            distances.append(d)

    return times, distances

#END OF DEF


def main():
    allFiles = glob.glob("geoJSONData\*")
    for file in allFiles:
        geo = gpd.read_file(file)
        frame = pd.DataFrame(geo)
        coordinates = getCoordinates(frame)
        times, distances = getTimeStampsAndDistance(frame)

        nparray = np.array(coordinates)
        times = np.array(times)
        newFrame = df(nparray, columns = ["lat", "long"])
        newFrame["timeStamp"] = times
        newFrame["Distance"] = distances
    
        name = file.replace("geoJSONData", "")
        name = name.replace(".geojson", "")
        path = "geoJSONCSV" + name + ".csv"

        newFrame.to_csv(path, index = False)


if __name__ == "__main__":
    main()
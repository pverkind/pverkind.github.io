"""
procedure:
1. in the Excel file Empire structure maps.xlsx, fill in
   a. the lines sheet:
   b. the points sheet
2. save each of these sheets separately as a Unicode text file
3. change the extension of these unicode text files to .csv
   (NB: the encoding of these files is utf-16, not utf-8)
4. add new places to the kml file
5. in QGIS, save the kml file as a csv file (encoding: utf-8)
6. run this python file to create the geojson files,
   which are then wrapped in javascript files to facilitate importing
"""

import simplekml
from openpyxl import *
from bs4 import BeautifulSoup

import datetime
import json
import copy

capital_types = {"imperial capital": {"marker_size" : 10,
                                      "marker_colour" : "green"
                                      },
                 "super-provincial capital" : {"marker_size" : 8,
                                               "marker_colour" : "green"
                                               },
                 "provincial capital" : {"marker_size" : 4,
                                         "marker_colour" : "green"
                                         },
                 "kura capital" : {"marker_size" : 2,
                                   "marker_colour" : "green"
                                   },
                 "independent capital" : {"marker_size" : 4,
                                          "marker_colour" : "red"
                                          },
                 }

geojson = {"type": "FeatureCollection",
           "features": [],
           }
geojson_feature =   {"type": "Feature",
                     "properties": {"name": "",
                                    "start": "", # yyyy-mm-dd
                                    "end": "",
                                    "ref": "",
                                    "marker_size": "",
                                    "marker_colour": "",
                                    "version": "",
                                    "version_date": "",
                                    },
                     "geometry": {"type": "", # Point or LineString
                                  "coordinates": [] # list for point, list of lists for line
                                  }
                     }
                        

control_types = {"intermittent":"",
                 "suzerainty":"",
                 }

def load_xlsx_sheet(fp, sheetname):
    wb = load_workbook(fp, data_only=True)
    ws = wb[sheetname]
    data = []
    for row in ws.rows:
        current_row = []
        for cell in row:
            current_row.append(cell.value)
        data.append(current_row)
    return data
    

def write_geojson(outpth, data):
    with open(outpth, mode="w", encoding="utf-16") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4, sort_keys=True)
        

def geojson2js(inpth, outpth, var_name):
    with open(inpth, mode="r", encoding="utf-16") as file:
        data = file.read()
    with open(outpth, mode="w", encoding="utf-16") as outfile:
        outfile.write("var {} = {}".format(var_name, data))
##    with open(outpth, "rb") as file:
##        data = file.read()    
##    with open(outpth, 'w+b') as outfile:
##        outfile.write(data.decode("utf-16").encode("utf-8"))


def load_kml_data(kml_fp):
    """X,Y,Name,description,"""
    with open(kml_fp, mode="r", encoding="utf-8") as file:
        s = BeautifulSoup(file, "xml")
    all_places = []
    for placemark in s.find_all("Placemark"):
        if placemark.find('coordinates'):
            coordinates = placemark.find('coordinates').string
            place = coordinates.split(",")[:2]
        if placemark.find('name'):
            name = placemark.find('name').string
        else:
            name = "None"
        place.append(name)
        if placemark.find('description'):
            description = placemark.find('description').string
        else:
            description = ""
        place.append(description)
        #print(place)
        all_places.append(place)
    return all_places


def load_coordinates(kml_fp, separator=",", encoding="utf-8"):
    """the coordinates csv has as first three columns lon, lat, name"""
    data = load_kml_data(kml_fp)
    coord = {}
    for i, line in enumerate(data):
        #print(i, line[2])
        coord[line[2]] = [float(line[0]), float(line[1])]
    return coord


def load_features(features_fp, sheetname, feature_type,
                  capital_types, coord, version, version_date,
                  separator="\t", encoding="utf-16"):
    """csv columns for Points:
    0: name
    1: capital_type
    2: latitude
    3: longitude
    4: from_date
    5: to_date
    6: from_date_converted
    7: to_date_converted
    8: ref
    9: notes
    10: marker_size
    11: marker_colour
    
    csv columns for PolyLines:
    0: from_place
    1: to_place
    2: from_date
    3: to_date
    4: from_date converted
    5: to_date converted
    6: line_thickness
    7: control_type
    8: ref
    9: notes
    """
    
    data = load_xlsx_sheet(features_fp, sheetname)
    #print(data[:3])
    geojson_coll = copy.deepcopy(geojson)
    #print(data[2])
    for i, line in enumerate(data[1:]):
        if line[0]:
            #print(geojson_feature)
            try: 
                feat = copy.deepcopy(geojson_feature)
                if feature_type == "Point":
                    #print(line[0])
                    feat["geometry"]["type"] = "Point"
                    feat["geometry"]["coordinates"] = coord[line[0]]
                    feat["properties"]["name"] = line[0]
                    feat["properties"]["capital_type"] = line[1]
                    feat["properties"]["start"] = line[6]
                    feat["properties"]["end"] = line[7]
                    feat["properties"]["ref"] = line[8]
                    if line[9]:
                        feat["properties"]["notes"] = line[9]
                    else:
                        feat["properties"]["notes"] = ""
                    feat["properties"]["marker_size"] = capital_types[line[1]]["marker_size"]
                    feat["properties"]["marker_colour"] = capital_types[line[1]]["marker_colour"]
                    feat["properties"]["version"] = version
                    feat["properties"]["version_date"] = version_date
                elif feature_type == "LineString":
                    feat["geometry"]["type"] = "LineString"
                    feat["geometry"]["coordinates"] = [coord[line[0]],
                                                       coord[line[1]]
                                                       ]
                    feat["properties"]["name"] = "{} - {}".format(line[0], line[1])
                    feat["properties"]["start"] = line[4]
                    feat["properties"]["end"] = line[5]
                    feat["properties"]["marker_size"] = (int(line[6])/3)*2
                    feat["properties"]["marker_colour"] = "green" ####
                    if line[5] in control_types:
                        feat["properties"]["line_style"] = control_types[line[7]]
                    else:
                        feat["properties"]["line_style"] = None ####
                    if line[9]:
                        feat["properties"]["notes"] = line[9]
                    else:
                        feat["properties"]["notes"] = ""
                    feat["properties"]["version"] = version
                    feat["properties"]["version_date"] = version_date
                else:
                    print("no feature type for line", line)
                geojson_coll["features"].append(feat)
            except:
                print("error in line", i, line)
    return geojson_coll


xlsx_fp = "data/Empire structure maps.xlsx"
kml_fp = "data/empire structure_cities.kml"

version = "1"
version_date = str(datetime.datetime.now())

coord = load_coordinates(kml_fp, separator=",", encoding="utf-8")
#print(coord)
points_geojson = load_features(xlsx_fp, "points", "Point",
                  capital_types, coord, version, version_date,
                  separator="\t", encoding="utf-16")
#print(points_geojson)
write_geojson("data/points.geojson", points_geojson)
lines_geojson = load_features(xlsx_fp, "lines", "LineString",
                  capital_types, coord, version, version_date,
                  separator="\t", encoding="utf-16")    
write_geojson("data/lines.geojson", lines_geojson)
geojson2js("data/lines.geojson", "data/import_lines_geojson.js", "linestrings")
geojson2js("data/points.geojson", "data/import_points_geojson.js", "points")        

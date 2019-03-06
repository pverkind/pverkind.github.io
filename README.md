# PowerLines
A map designed to represent shifting power structures in the early Islamic empire.

Power structure data is entered in an Excel file (data/Empire structure maps.xlsx); each sheet is saved as a csv (in fact, tsv) file. 

Coordinates are provided by a kml file (data/empire structure_cities.kml), which is converted into a csv file in QGIS. 

Data is then extracted from the three csv files by a Python script (data/csv2geojson.py) and converted to geojson files. These are then packaged as javascript files to facilitate importing into the html file (PowerLines.html).

# To do: 
* improve the data.
* make the Python file read data from the xlsx and kml files directly, without intermediate conversions to csv.

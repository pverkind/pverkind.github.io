# PowerLines
A map designed to represent shifting power structures in the early Islamic empire.

Power structure data is entered in an Excel file (data/Empire structure maps.xlsx). 

Coordinates are provided by a kml file (data/empire structure_cities.kml). 

Data is then extracted from the three xlsx and kml files by a Python script (xlsx2geojson.py) and converted to geojson files. These are then packaged as javascript files to facilitate importing into the html file (PowerLines.html).

# To do: 
* improve the data
* improve the visualization
* add more levels of government control

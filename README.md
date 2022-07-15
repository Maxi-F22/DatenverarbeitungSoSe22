# DatenverarbeitungSoSe22

## Thema: Mittelalterstadt aus echten Kartendaten erstellen
Felix Iltgen, Maximilian Flack

## Beschreibung des Projekts:
Dieses Projekt generiert aus Kartendaten, die von Open Street Map exportiert wurden, eine mittelalterliche Stadt.
Dabei werden Häuser und Straßen auf die realen Standorte von der OSM-Map gesetzt und die eingetragenen Waldstücke mit verschiedenen Baum-Assets gefüllt.

## Installation:
Benötigte Software:
Blender (getestet mit 3.1.0)

### Module in Blender Python installieren:
- Osmium
- Shapely

Dafür in shell (z.B. Powershell):
```
cd /path/to/blender/python/bin
./python -m ensurepip
./python -m pip install osmium
./python -m pip install Shapely
```

*Hinweis:
Teilweise gibt es das Problem, dass die Modulordner nicht in das richtige Verzeichnis gelegt werden bei der Installation.
Falls dies vorkommt, von Hand die Modulordner in das folgende Verzeichnis legen:
/path/to/blender/python/lib/site-packages*

### Schritte zur Installation:
1. Dieses Repository in einen beliebigen Ordner klonen
2. Den Ordner "Assets" kopieren und in den Ordner: "Blender" im Verzeichnis "C:\Users\MYNAME\Documents" kopieren (Falls der Ordner "Blender" nicht vorhanden ist, neu erstellen)
3. Blender starten
4. In *Edit/Preferences/Add-ons* auf "Install" klicken
5. Die Datei "CityTransformator.py" aus dem Repository-Ordner auswählen
6. Das Add-on aktivieren
7. Im Viewport von Blender F3 drücken und den "City Transform Operator" auswählen

Falls ein anderer Kartenausschnitt benutzt werden soll, kann man auf [Open Street Map](https://www.openstreetmap.org/) einen Ausschnitt exportieren und diesen in den Assets Ordner in Documents kopieren. Die Datei muss den Namen "map.osm" haben. Der Kartenausschnitt sollte nicht zu groß gewählt werden. Nachdem eine neue Map in den Ordner Assets gelegt wurde, muss das Add-On neu in Blender reingeladen werden.

### Benutzung des Add-Ons:
1. Nachdem es in Blender mit F3 geladen wurde, erscheint rechts ein Panel
2. Auf Panel Einstellungen festlegen
3. Stadt generieren

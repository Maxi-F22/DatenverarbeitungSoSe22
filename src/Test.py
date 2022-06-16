import bpy

#Latitude is Z axis
#Longitude is Y axis

def map(maplength, mapwidth, lat_south, lat_north, long_west, long_east, list):
    lat_calc = (maplength) / (lat_north - lat_south)
    print(lat_calc)
    long_calc = (mapwidth) / -((long_west - long_east))
    print(long_calc)
    a = 0
    while a < len(list):
        alat = float(list[a+2])-lat_south
        along = float(list[a+3]) - long_west
        x=0
        y = long_calc * along
        z = lat_calc * alat
        bpy.ops.mesh.primitive_uv_sphere_add(size=0.02, location=(x,y,z))
        a = a + 4
#End of function but can't get WordPress to indent properly
caps = ["Alabama", "Montgomery", "32.3617", "-86.2792", "Arizona", "Phoenix", "33.45", "-112.067", "Arkansas", "Little Rock", "34.7361", "-92.3311", "California", "Sacramento", "38.5556", "-121.469", "Colorado", "Denver", "39.7618", "-104.881", "Connecticut", "Hartford", "41.7627", "-72.6743", "Delaware", "Dover", "39.1619", "-75.5267", "Florida", "Tallahassee", "30.455", "-84.2533", "Georgia", "Atlanta", "33.755", "-84.39", "Idaho", "Boise", "43.6167", "-116.2", "Illinois", "Springfield", "39.6983", "-89.6197", "Indiana", "Indianapolis", "39.791", "-86.148", "Iowa", "Des Moines", "41.5908", "-93.6208", "Kansas", "Topeka", "39.0558", "-95.6894", "Kentucky", "Frankfort", "38.197", "-84.863", "Louisiana", "Baton Rouge", "30.45", "-91.14", "Maine", "Augusta", "44.307", "-69.782", "Maryland", "Annapolis", "38.9729", "-76.5012", "Massachusetts", "Boston", "42.3581", "-71.0636", "Michigan", "Lansing", "42.7336", "-84.5467", "Minnesota", "Saint Paul", "44.9442", "-93.0936", "Mississippi", "Jackson", "32.2989", "-90.1847", "Missouri", "Jefferson City", "38.5767", "-92.1736", "Montana", "Helena", "46.5958", "-112.027", "Nebraska", "Lincoln", "40.8106", "-96.6803", "Nevada", "Carson City", "39.1608", "-119.754", "New Hampshire", "Concord", "43.2067", "-71.5381", "New Jersey", "Trenton", "40.2237", "-74.764", "New Mexico", "Santa Fe", "35.6672", "-105.964", "New York", "Albany", "42.6525", "-73.7572", "North Carolina", "Raleigh", "35.7667", "-78.6333", "North Dakota", "Bismarck", "46.8133", "-100.779", "Ohio", "Columbus", "39.9833", "-82.9833", "Oklahoma", "Oklahoma City", "35.4822", "-97.535", "Oregon", "Salem", "44.9308", "-123.029", "Pennsylvania", "Harrisburg", "40.2697", "-76.8756", "Rhode Island", "Providence", "41.8236", "-71.4222", "South Carolina", "Columbia", "34.0006", "-81.0347", "South Dakota", "Pierre", "44.368", "-100.336", "Tennessee", "Nashville", "36.1667", "-86.7833", "Texas", "Austin", "30.25", "-97.75", "Utah", "Salt Lake City", "40.75", "-111.883", "Vermont", "Montpelier", "44.2597", "-72.575", "Virginia", "Richmond", "37.5333", "-77.4667", "Washington", "Olympia", "47.0425", "-122.893", "West Virginia", "Charleston", "38.3472", "-81.6333", "Wisconsin", "Madison", "43.0667", "-89.4", "Wyoming", "Cheyenne", "41.1456", "-104.802"]

ml = 2.88135
ls = 25.119
ln = 49.006
mw = 6.98
lw = -124.733
le = -66.951

map(ml, mw, ls, ln, lw, le, caps)
import overpy

api = overpy.Overpass()

# fetch all ways and nodes
result = api.query("""
    area["name"="United Kingdom"]->.boundaryarea;
(
 nwr(area.boundaryarea)[landuse="port"];
 nwr(area.boundaryarea)[landuse="harbour"];
);
out center;
    """)

for way in result.ways:
    print("Name: %s" % way.tags.get("name", "n/a"))
    print("  Highway: %s" % way.tags.get("highway", "n/a"))
    print("  Nodes:")
    for node in way.nodes:
        print("    Lat: %f, Lon: %f" % (node.lat, node.lon))
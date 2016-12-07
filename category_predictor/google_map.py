from flask_googlemaps import Map

@app.route("/gmap")
def mapview():
    mymap = Map(
        identifier="cluster-map",
        lat=37.4419,
        lng=-122.1419,
        markers=[{'lat': 37.4419, 'lng': -122.1419}, {'lat': 37.4500, 'lng': -122.1419}, {'lat': 36.4419, 'lng': -120.1419}]
        cluster=True,
        cluster_gridsize=10
    )
    return render_template('clustermap.html', clustermap=clustermap)

Template:
in head:
    {{clustermap.js}}
in body:
    {{clustermap.html}}

let baseballIcon = L.icon({
    iconUrl: "static/icons/baseball-ball-solid.svg",
    iconSize: [32, 32],
    iconAnchor: [12, 12],
    popupAnchor: [0, 0]
});

let map = L.map("viewer-map", {
    zoom: 3
});

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

fetch("InsideBaseball.geojson")
    .then(response => {
        return response.json();
    })
    .then(data => {
        L.geoJSON(data, {
            onEachFeature: (feature, layer) => {
                let popup = `
                <h1>${feature.properties.title}</h1>

                <div>${feature.properties.metadata.Description}</div>

                `.trim();

                if (feature.properties.metadata.Copyright) {
                    popup += `<div><b>Copyright:</b> ${
                        feature.properties.metadata.Copyright
                    }</div>`;
                }

                layer.bindPopup(popup.trim());
            },
            pointToLayer: (feature, latlng) => {
                return L.marker(latlng, {
                    title: feature.properties.title
                });
            }
        }).addTo(map);
    });

fetch(
    "https://raw.githubusercontent.com/cageyjames/GeoJSON-Ballparks/master/ballparks.geojson"
)
    .then(response => {
        return response.json();
    })
    .then(data => {
        let ballparksLayer = L.geoJSON(data, {
            pointToLayer: (feature, latlng) => {
                let props = feature.properties,
                    title = `${props.Ballpark} (${props.Team})`;

                return L.marker(latlng, {
                    icon: baseballIcon,
                    title: title
                });
            }
        });

        ballparksLayer.addTo(map);

        // Now that we have a layer, we'll add a control for toggling them:
        L.control.layers(null, { "Present Day Ballparks": ballparksLayer }).addTo(map);
    });

map.setView({ lat: 38.8879105, lng: -77.0024652 }, 7);


// Map and its initialization.

var map;
var location_timeout = 4000;

function add_markers(map) {
    let lat = 37.462910;
    let lng = -121.997299;
    let latlng = new google.maps.LatLng(lat, lng);
    var marker = new google.maps.Marker({
        position: latlng,
        title: "Great Blue Heron"
    });
    const infowindow = new google.maps.InfoWindow({
        content: '<h1 class="is-size-5 has-text-weight-semibold">Great Blue Heron</h1>'
    });
    marker.addListener("click", () => {
        infowindow.open(map, marker);
    })
    marker.setMap(map);
}


// This will be the object that will contain the Vue attributes
// and be used to initialize it.
var app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init_vue = (app) => {

    // We initialize it later.
    app.marker_button = null;
    app.map = null;
    app.marker = null;

    // This is the Vue data.
    app.data = {
        search_text: ""
    };

    app.map_search = function (e) {
        if (e.keyCode === 13) {
            let requrl = "https://maps.googleapis.com/maps/api/geocode/json?";
            requrl += "key=" + maps_api_key;
            requrl += "&address=" + encodeURIComponent(app.vue.search_text);
            console.log(requrl);
            axios.get(requrl).then(function (response) {
                console.log(response);
                if (response.status === 200 && response.data.status === "OK") {
                    if (response.data.results.length > 0) {
                        let first_result = response.data.results[0];
                        let lat = first_result.geometry.location.lat;
                        let lng = first_result.geometry.location.lng;
                        app.map.setCenter({lat: lat, lng: lng});
                        app.map.setZoom(14);
                    }
                }
            });
        }
    };

    app.edit_loc = function (loc_idx) {
        // TODO
    };

    app.reindex_locations = function (locations) {
        let idx = 0;
        for (let loc of locations) {
            loc._idx = idx++;
            loc.is_active = false;
            loc.is_edited = false;
        }
        return locations;
    };

    app.load_locations = function () {
        // Gets the current bounds, and loads the locations.
        let bounds = app.map.getBounds();
        let ne = bounds.getNorthEast();
        let sw = bounds.getSouthWest();
        axios.get(callback_url, {
            params: {
                lat_max: ne.lat, lat_min: sw.lat,
                lng_max: sw.lng, lng_min: ne.lng
            }}).then(function (response) {
                if (response.status === 200) {
                    app.vue.locations = app.reindex_locations(response.data.locations);
                }
        });
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        map_search: app.map_search,
        edit_loc: app.edit_loc
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
    };

    // Map setter.
    app.set_map = function (map) {
        app.map = map;
        // Gets the list of locations.
        app.load_locations();
    };

    // Call to the initializer.
    app.init();
};

init_vue(app); // Init Vue.


function initMap() {
    // Can we find the latest location from localstorage?
    let lat = 37;
    let lng = -120;
    let zoom = 6;
    let local_storage = window.localStorage;
    let loc_str = local_storage.getItem("latlong");
    if (loc_str) {
        let loc = JSON.parse(loc_str);
        lat = loc.lat;
        lng = loc.lng;
        zoom = loc.zoom;
    }
    map = new google.maps.Map(
        document.getElementById('map'), {
            center: {lat: lat, lng: lng},
            zoom: zoom,
            mapTypeControl: false,
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.BOTTOM_LEFT,
            }
        });
    app.set_map(map);
}


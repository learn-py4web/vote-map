
// Map and its initialization.

var info_window;
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


function add_location_button(map) {
    // Adds button to go to current location.
    let control_div = document.createElement('div');
    let location_button = document.createElement('button');
    location_button.style.backgroundColor = '#fff';
    location_button.style.border = 'none';
    location_button.style.outline = 'none';
    location_button.style.borderRadius = '2px';
    location_button.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
    location_button.style.cursor = 'pointer';
    location_button.style.margin = '10px';
    location_button.style.padding = '10px';
    location_button.style.width = '40px';
    location_button.title = 'Your Location';
    control_div.appendChild(location_button);

    let location_icon = document.createElement('i');
    location_icon.classList.add('fa', 'fa-2x', 'fa-crosshairs');
    location_button.appendChild(location_icon);

    location_button.addEventListener('click', function() {
        if(navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                var marker = new google.maps.Marker({
                    map: map,
                    animation: google.maps.Animation.DROP,
                    position: latlng
                });
                marker.setPosition(latlng);
                map.setCenter(latlng);
            }, function () {}, {timeout: location_timeout});
        }
        else{
        }
    });

    control_div.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(control_div);
}

function geolocate(info_window, map) {
// Try HTML5 geolocation.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            console.log("Gotten position:", position.coords)
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            info_window.setPosition(pos);
            info_window.setContent('Location found.');
            info_window.open(map);
            map.setCenter(pos);
        }, function () {
            handleLocationError(true, info_window, map.getCenter());
        },
            {timeout: location_timeout});
    } else {
        console.log("Location could not be determined.");
    }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    console.log("Location could not be determined.");
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
        }
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        map_search: app.map_search
    };

    app.add_marker_button = function (mapref) {
        // Adds a dropoff marker.
        app.marker_button = add_dropoff_maker_button(mapref, app);
        app.map = mapref;
    };

    app.clicked_marker_button = function () {
        // Handle click of button to add marker.
        console.log("clicked");
        // Puts a marker in the map center.
        let c = app.map.getCenter();
        app.marker = new google.maps.Marker({
            position: c,
            draggable: true,
            label: 'A'
        });
        app.marker.setMap(app.map);
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

    // Call to the initializer.
    app.init();
};

init_vue(app); // Init Vue.

function add_dropoff_maker_button(map, vue_app) {
    // Adds button to create a new dropoff location.
    let control_div = document.createElement('div');
    let add_marker_button = document.createElement('button');
    add_marker_button.style.backgroundColor = '#f55';
    add_marker_button.style.border = 'none';
    add_marker_button.style.outline = 'none';
    add_marker_button.style.borderRadius = '2px';
    add_marker_button.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
    add_marker_button.style.cursor = 'pointer';
    add_marker_button.style.margin = '10px';
    add_marker_button.style.padding = '12px';
    add_marker_button.style.width = '40px';
    add_marker_button.title = 'Add ballot dropoff';
    control_div.appendChild(add_marker_button);

    let marker_icon = document.createElement('i');
    marker_icon.classList.add('fa', 'fa-2x', 'fa-map-marker');
    add_marker_button.appendChild(marker_icon);

    add_marker_button.addEventListener('click', function() {
        // Click listener for creating new marker.
        vue_app.clicked_marker_button();
    });

    control_div.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(control_div);
    return add_marker_button;
}

function initMap() {
    map = new google.maps.Map(
        document.getElementById('map'), {
            center: {lat: 37, lng: -120},
            zoom: 6,
            mapTypeControl: false,
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.BOTTOM_LEFT,
            }
        });
    info_window = new google.maps.InfoWindow();
    geolocate(info_window, map);
    add_location_button(map);
    // add_markers(map);
    app.add_marker_button(map);
}

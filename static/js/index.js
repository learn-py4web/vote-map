
// Map and its initialization.

var info_window;
var map;
var location_timeout = 4000;

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

    addYourLocationButton(map);
}


function addYourLocationButton(map)
{
    var controlDiv = document.createElement('div');

    var location_button = document.createElement('button');
    location_button.style.backgroundColor = '#fff';
    location_button.style.border = 'none';
    location_button.style.outline = 'none';
    location_button.style.borderRadius = '2px';
    location_button.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
    location_button.style.cursor = 'pointer';
    location_button.style.marginRight = '10px';
    location_button.style.padding = '10px';
    location_button.title = 'Your Location';
    controlDiv.appendChild(location_button);

    var location_icon = document.createElement('i');
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

    controlDiv.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(controlDiv);
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
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
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

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

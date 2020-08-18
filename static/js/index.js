
// Map and its initialization.

var infoWindow;
var map;

function initMap() {
    map = new google.maps.Map(
        document.getElementById('map'), {
          center: {lat: 37, lng: -120},
          zoom: 6
        });
    infoWindow = new google.maps.InfoWindow();
    geolocate(infoWindow, map);
}

function geolocate(infoWindow, map) {
// Try HTML5 geolocation.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            console.log("Gotten position:", position.coords)
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            infoWindow.setPosition(pos);
            infoWindow.setContent('Location found.');
            infoWindow.open(map);
            map.setCenter(pos);
        }, function () {
            handleLocationError(true, infoWindow, map.getCenter());
        },
            {timeout: 2000});
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

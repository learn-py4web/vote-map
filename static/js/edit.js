
// Map and its initialization.

var map;

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
var app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init_vue = (app) => {

    app.map = null; // The map
    app.initial_load = true; // To load locations initially only.
    app.edited_idx = null;
    app.fields = [];

    // This is the Vue data.
    app.data = {
        search_text: "",
        locations: [],
        mode: "browse", // "browse" or "edit".
        include_deleted: false, // Include deleted locations when editing.
        // Fields.
        eloc: {},
        maybe_incomplete: false, // Zoom in to see all data.
    };

    app.computed = {
        is_modified: function () {
            if (app.vue.mode === "browse") { return false; }
            if (!app.vue.eloc) { return false; }
            try {
                let loc = app.vue.locations[app.edited_idx];
                for (const p of app.fields) {
                    if (app.vue.eloc[p] !== loc[p]) {
                        return true;
                    }
                }
                return false;
            } catch (e) {
                return true;
            }
        }
    }

    app.map_center = function (e) {
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

    app.add_loc = function () {
        // Adds a new location.
        app.vue.mode = "edit";
        app.hide_markers();
        // Creates a new empty location.
        let loc = {};
        for (const p of app.fields) {
            loc[p] = null;
        }
        loc.is_deleted = false;
        // Copies it into eloc to allow editing.
        app.vue.eloc = {};
        for (const p of app.fields) {
            Vue.set(app.vue.eloc, p, loc[p]);
        }
        // Puts a marker in the center.
        let c = app.map.getCenter();
        app.vue.eloc.lat = c.lat();
        app.vue.eloc.lng = c.lng();
        let marker_options = {
            position: {lat: c.lat(), lng: c.lng()},
            map: app.map,
            draggable: true,
        }
        loc.marker = new google.maps.Marker(marker_options);
        loc.marker.addListener('dragend', function () {
            let l = loc.marker.getPosition();
            app.vue.eloc.lat = l.lat();
            app.vue.eloc.lng = l.lng();
        });
        // Adds the location.
        app.edited_idx = app.vue.locations.length;
        app.vue.locations.push(loc);
    };

    app.edit_loc = function (idx) {
        // Starts the edit of a location.
        let loc = app.vue.locations[idx];
        app.edited_idx = idx;
        app.hide_all_but_one_marker(idx);
        app.vue.mode = "edit";
        // Loads the edit fields.
        app.vue.eloc = {};
        for (const p of app.fields) {
            Vue.set(app.vue.eloc, p, loc[p]);
        }
        // Makes the marker draggable.
        loc.marker.setDraggable(true);
        // loc.marker.setAnimation(google.maps.Animation.BOUNCE);
        loc.marker.setLabel(null);
        loc.marker.addListener('dragend', function () {
            let l = loc.marker.getPosition();
            app.vue.eloc.lat = l.lat();
            app.vue.eloc.lng = l.lng();
        });

    };

    app.cancel_edit = function () {
        app.edited_idx = null;
        app.vue.mode = "browse";
        app.remove_markers();
        app.load_locations();
    };

    app.save_edit = function () {
        let loc = app.vue.locations[app.edited_idx];
        for (const p of app.fields) {
            Vue.set(loc, p, app.vue.eloc[p]);
        }
        app.edited_idx = null;
        app.vue.mode = "browse";
        // Sends the edit.
        let send_loc = {}
        for (const p of app.fields) {
            send_loc[p] = loc[p];
        }
        send_loc.is_vote = false;
        axios.post(callback_url, send_loc);
        // Resets the markers.
        app.remove_markers();
        // Reloads the locations, as one might have moved the map.
        app.load_locations();
    };

    app.confirm = function () {
        axios.post(callback_url,
            {is_vote: true, id: app.vue.eloc.id});
        app.edited_idx = null;
        app.vue.mode = "browse";
        app.remove_markers();
        app.load_locations();
    }

    app.show_markers = function () {
        for (let loc of app.vue.locations) {
            if (loc.marker) {
                loc.marker.setMap(app.map);
            }
        }
    };

    app.hide_markers = function () {
        for (let loc of app.vue.locations) {
            if (loc.marker) {
                loc.marker.setMap();
            }
        }
    };

    app.remove_markers = function () {
        // Removes the old markers.
        app.hide_markers();
        for (const loc of app.vue.locations) {
            loc.marker = null;
        }
    }

    app.hide_all_but_one_marker = function (idx) {
        for (let i = 0; i < app.vue.locations.length; i++) {
            if (app.vue.locations[i].marker) {
                if (i === idx) {
                    app.vue.locations[i].marker.setMap(app.map);
                } else {
                    app.vue.locations[i].marker.setMap();
                }
            }
        }
    };

    app.load_locations_once = function () {
        if (app.initial_load) {
            app.initial_load = false;
            app.load_locations();
        }
    };

    app.map_moved = function () {
        // The map moved.  Stores the new location in local storage.
        try {
            let c = app.map.getCenter();
            let z = app.map.getZoom();
            window.localStorage.setItem("latlong", JSON.stringify({
                lat: c.lat(),
                lng: c.lng(),
                zoom: z
            }));
        } catch (e) {}
        // If we are browsing, loads the new locations.
        if (app.vue.mode == "browse") {
            app.load_locations();
        }
    }

    app.toggle_deleted = function () {
        let loc = app.vue.locations[app.edited_idx];
        let marker_options = {
            position: {lat: loc.lat, lng: loc.lng},
            map: app.map,
            draggable: true,
            // animation: google.maps.Animation.BOUNCE,
        };
        if (app.vue.eloc.is_deleted) {
            marker_options.icon = app.deleted_icon;
        }
        loc.marker.setMap();
        loc.marker = new google.maps.Marker(marker_options);
        loc.marker.setMap(map);
    }

    app.reindex_locations = function (locations) {
        let idx = 0;
        let new_locations = [];
        for (let loc of locations) {
            if (app.vue.include_deleted || !loc.is_deleted) {
                loc._idx = idx++;
                loc.label = idx.toString();
                loc.is_active = false;
                loc.is_edited = false;
                // Creates a marker for displaying the location.
                let marker_options = {
                    position: {lat: loc.lat, lng: loc.lng},
                    map: app.map,
                    label: loc.label
                };
                loc.marker = null;
                if (loc.is_deleted) {
                    marker_options.icon = app.deleted_icon;
                    loc.marker = new google.maps.Marker(marker_options);
                } else {
                    loc.marker = new google.maps.Marker(marker_options);
                }
                loc.marker.addListener('click', function () {
                    app.edit_loc(loc._idx);
                });
            new_locations.push(loc);
            }
        }
        return new_locations;
    };

    app.load_locations = function () {
        // Gets the current bounds, and loads the locations.
        let bounds = app.map.getBounds();
        let ne = bounds.getNorthEast();
        let sw = bounds.getSouthWest();
        axios.get(callback_url, {
            params: {
                lat_max: ne.lat(), lat_min: sw.lat(),
                lng_min: sw.lng(), lng_max: ne.lng(),
                include_deleted: app.vue.include_deleted,
            }}).then(function (response) {
                if (response.status === 200) {
                    // Removes the old markers.
                    app.hide_markers();
                    for (const loc of app.vue.locations) {
                        loc.marker = null;
                    }
                    // Builds the new location list.
                    let all_locations = response.data.locations.concat(response.data.deleted_locations);
                    app.vue.locations = app.reindex_locations(all_locations);
                    app.fields = response.data.fields;
                    app.vue.maybe_incomplete = response.data.maybe_incomplete;
                }
        });
    };

    app.display_locations = function () {
        // Displays all locations.
        for (let loc of app.vue.locations) {
            app.display_location(loc);
        }
    };

    app.display_location = function (loc) {
        // displays location loc on the map.
    }

    app.move_marker_to_address = function () {
        // TODO
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        map_center: app.map_center,
        edit_loc: app.edit_loc,
        add_loc: app.add_loc,
        move_marker_to_address: app.move_marker_to_address,
        cancel_edit: app.cancel_edit,
        save_edit: app.save_edit,
        confirm: app.confirm,
        load_locations: app.load_locations,
        toggle_deleted: app.toggle_deleted,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        computed: app.computed,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
    };

    // Map setter.
    app.set_map = function (map) {
        app.map = map;
        // Yes, it's silly, but there is no init event that tells us
        // when the map is loaded.  So we listen to bounds_changed, but
        // only once, and we load the locations.  Otherwise, we load the
        // locations only on drag_end, to save on loads.
        map.addListener('bounds_changed', app.load_locations_once);
        map.addListener('dragend', app.map_moved);
        map.addListener('zoom_changed', app.map_moved);
        // We cannot do this before, because 'google' is not defined.
        app.deleted_icon = {
            url: "images/purple-blank.png",
            size: new google.maps.Size(44, 44),
            labelOrigin: new google.maps.Point(22, 14),
        };

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
    try {
        let local_storage = window.localStorage;
        let loc_str = local_storage.getItem("latlong");
        if (loc_str) {
            let loc = JSON.parse(loc_str);
            lat = loc.lat;
            lng = loc.lng;
            zoom = loc.zoom;
        }
    } catch (e) {}
    map = new google.maps.Map(
        document.getElementById('map'), {
            center: {lat: lat, lng: lng},
            zoom: zoom,
            mapTypeControl: true,
            streetViewControl: false,
            fullscreenControl: false,
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.BOTTOM_LEFT,
            }
        });
    app.set_map(map);
}


var map = "";
var markerCluster;
var marker_list = [];
var geo_list = [];
var infowindow = '';
var min_zoom_level = 2;

// Initialize Google map
function initMap() {
  var nyc = {lat: 40.7128, lng: -74.0059}; 
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 4,
    center: nyc
  });
  infowindow = new google.maps.InfoWindow({});
  limit_zoom_level();
}

function load_tweet(list) {
	var object_list = list.hits.hits; 
	console.log(JSON.stringify(object_list));
	for (var i = 0; i < object_list.length; i++) {
		curr_latitude = object_list[i]._source.location[1];
		curr_longitude = object_list[i]._source.location[0];
		drop_marker(curr_latitude, curr_longitude, object_list[i]._source);
	}
    /*
        markerCluster = new MarkerClusterer(map, marker_list,
        {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
	*/
}

function drop_marker(latitude, longitude, source_object) {
	var curr_lat_and_lng = {lat: latitude, lng: longitude};
	var new_marker = new google.maps.Marker({
    	position: curr_lat_and_lng,
    	map: map
  	});
  	new_marker.addListener('click', function() {
  		toggleMarker(source_object);
  		infowindow.open(map, new_marker);
  	});
  	marker_list.push(new_marker);

}

function placeMarker(location) {
    clearGeoTags();
    var markerColor = '0000FF';
    var markerImage = new google.maps.MarkerImage(
        "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + markerColor,
        new google.maps.Size(80, 400),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34));
    var marker = new google.maps.Marker({
        position: location,
        map: map,
        title: "Tweets around this area",
        icon: markerImage
    });
    geo_latitude = marker.getPosition().lat();
    geo_longitude = marker.getPosition().lng();
    geo_list.push(marker);
    search_by_geo_distance(geo_latitude, geo_longitude)
}

function toggleMarker(source_object) {
	var contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '</div>'+
            '<h1 id="firstHeading" class="firstHeading"></h1>'+
            '<div id="bodyContent">'+
            '<p>' + source_object.message + '</p>' +
            '<b>' + source_object.author + '</b>' +
            '<p>' + source_object.timestamp + '</p>' +
            '</div>'+
            '</div>';
	infowindow.setContent(contentString); 
}

function get_type(thing){
    if(thing===null)return "[object Null]"; // special case
    return Object.prototype.toString.call(thing);
}

function search_by_geo_distance(latitude, longitude) {
	clearMarkers();
    var selected_key = $('#selected_keyword').value;
	var selected_dist = $('#selected_distance').value;
    //Here is where the ajax call is made i.e. where we then call the endpoint associated with the search function
	console.log(selected_distance.value);
	$.ajax({
		url: '/search/' + selected_keyword.value + '/' + selected_distance.value + '/' + latitude + '/' + longitude,
		type: 'GET',
		success: function(response) {
			console.log(JSON.stringify(response));
			load_tweet(response);
		},
		error: function(error) {
			console.log(JSON.stringify(error));
			$('#testing').text(JSON.stringify(error));
		}
	});
}

function search_by_keyword() {
	var selected_key = $('#selected_keyword').value;
    //Here is where the ajax call is made i.e. where we then call the endpoint associated with the search function
	console.log(selected_keyword.value);
	$.ajax({
		url: '/search/' + selected_keyword.value,
		type: 'GET',
		success: function(response) {
			load_tweet(response);
		},
		error: function(error) {
			console.log(JSON.stringify(error));
			$('#testing').text(JSON.stringify(error));
		}
	});
}

function clearMarkers(){
	for (var i = 0; i < marker_list.length; i++) {
          marker_list[i].setMap(null);
    }
}

function clearGeoTags(){
	for (var i = 0; i < geo_list.length; i++) {
          geo_list[i].setMap(null);
    }
}

function limit_zoom_level() {
	google.maps.event.addListener(map, 'zoom_changed', function () {
    	if (map.getZoom() < min_zoom_level) {
    		map.setZoom(min_zoom_level);
    	}
 	});
}

//Here is where, when we hit submit on the form, we get the keyword the user selected
$(document).ready(function() {
	initMap();

    google.maps.event.addListener(map, 'click', function(event) {
        placeMarker(event.latLng);
    });

	document.getElementById('keyword_select_form').addEventListener('submit', function (e) {
		e.preventDefault();
		clearMarkers();
		search_by_keyword();

	}, false);

});


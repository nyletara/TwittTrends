var map = "";
var markerCluster;
var marker_list = [];
var geo_list = [];
var infowindow = '';
var min_zoom_level = 2;

// close alert window in 2 seconds
/* function tempAlert(msg,duration)
{
	var el = document.createElement("div");
 	el.setAttribute("style","position:absolute;top:40%;left:20%;background-color:white;");
 	el.innerHTML = msg;
 	setTimeout(function(){
  		el.parentNode.removeChild(el);
 	},duration);
 	document.body.appendChild(el);
} */

function temp_alert() {
	console.log("Notification receieved");
	//$("#success-alert").show();
	//sleep(2000);
	//$("#success-alert").hide();
}

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

// Need to handle sentiment from here
function load_tweet(list) {
	var object_list = list.hits.hits; 
	console.log("########################################");
	console.log(JSON.stringify(object_list));
	console.log("########################################");
	for (var i = 0; i < object_list.length; i++) {
		curr_latitude = object_list[i]._source.location[1];
		curr_longitude = object_list[i]._source.location[0];
		// drop_marker(curr_latitude, curr_longitude, object_list[i]._source);
		// get sentiment here and pass it into the drop marker function
		sentiment = object_list[i]._source.sentiment;
		console.log("#######################################");
		console.log("adding sentiment - " + sentiment);
		console.log("#######################################");
		drop_marker(curr_latitude, curr_longitude, object_list[i]._source, sentiment);
	}
    /*
        markerCluster = new MarkerClusterer(map, marker_list,
        {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
	*/
}

function get_sentiment_color(sentiment) {
	var color;
	console.log("********************************");
	console.log(sentiment);
	console.log("********************************");
	if(sentiment == 'positive') {
		color = 'F95353';
	}
	else if (sentiment == 'negative') {
		color = '010101';
	} 
	else if (sentiment == 'neutral') {
		color = '6978FE';
	} 
	else {
		color = 'FEF4F4';
	}
	console.log(color);
	console.log("********************************");
	return color;
}

function drop_marker(latitude, longitude, source_object, sentiment) {
//function drop_marker(latitude, longitude, source_object) {
	var curr_lat_and_lng = {lat: latitude, lng: longitude};
	var marker_color = get_sentiment_color(sentiment);
	var markerImage = new google.maps.MarkerImage(
		"http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + marker_color,
		new google.maps.Size(80, 400),
	      	new google.maps.Point(0,0),
	        new google.maps.Point(10, 34));

	var new_marker = new google.maps.Marker({
    		position: curr_lat_and_lng,
    		map: map,
		icon: markerImage
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

function wait_notification() {
	console.log("in wait_notificaton!"); 
	$.ajax({
		url: '/search/sns',
		type: 'GET',
		success: function() {
			console.log("successfully alter");
			// alter("You have receive new twitt!");
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
	// NEED EXTRA TARGET HERE BEFOTE 'addEventListener'
	/*	document.getElementById('map').addEventListener('load', function(e){
		e.preventDefault();
		wait_notification();
	}, false); */	

    	google.maps.event.addListener(map, 'click', function(event) {
        	placeMarker(event.latLng);
    	});
	
	// the entire document will always wait for notification

	document.getElementById('keyword_select_form').addEventListener('submit', function (e) {
		e.preventDefault();
		clearMarkers();
		search_by_keyword();

	}, false);

});


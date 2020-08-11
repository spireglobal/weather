// add the selected WMS layer to the map
// after removing the current one
function addWMSLayer(layer_name, style, layer_index, times, legend_url) {
	if (window.Current_WMS_Layer[layer_index] || layer_name == 'none') {
		// remove existing WMS layera
		window.map.removeLayer('spire-wms-layer-' + layer_index);
		window.map.removeSource('spire-wms-source-' + layer_index);
		// remove this layer index from the global WMS state
		delete window.Current_WMS_Layer[layer_index];
		// check if another WMS layer is still instantiated
		var layer_exists = Object.keys(window.Current_WMS_Layer).length > 0;
		// if no other layer is instantiated, hide the WMS tools
		if (!layer_exists) {
			// hide WMS time controls
			document.getElementById('wms_time_controls').style.display = 'none';
			// stop time playback
			stopWMS();
		}
	}
	if (layer_name != 'none') {
		var time = window.WMS_Animation_Current_Time;
		// check if a WMS layer has already been added
		var layer_exists = Object.keys(window.Current_WMS_Layer).length > 0;
		if (!layer_exists) {
			// no other WMS layer is currently instantiated
			// so first we set the available times
			window.WMS_Animation_Times = times;
			// configure the UI slider maximum value
			// with the highest index value of the times array
			var max_time_index = times.length - 1;
			document.getElementById('wms_time_slider').max = max_time_index;
			// if no time is set, set time to the earliest available
			if (!time) {
				time = times[0];
			}
			// set global variable to keep track of WMS animation current time state
			window.WMS_Animation_Current_Time = time;
			// display the current WMS time
			changeWMSTimeDisplay(time);
			// make WMS time controls visible
			document.getElementById('wms_time_controls').style.display = 'block';
		}
		// build the WMS layer configuration
		var url = buildWMSLayerRequest(layer_name, style, layer_index, time);
		// add the WMS layer to the Mapbox basemap
		addLayerToMap(layer_index, url);
		// // add the WMS layer to the OpenLayers map
		// window.ol_map.addLayer(layer);
		// make legend button visible
		document.getElementById('show_legend_' + layer_index).style.display = 'inline-block';
		// add legend image to popup div
		document.getElementById('legend_wms_' + layer_index).style.backgroundImage = 'url(' + legend_url + ')';
	}
}

// configure a new WMS layer
// for reference: https://openlayers.org/en/latest/examples/wms-time.html
function buildWMSLayerRequest(layer_name, style, layer_index, time) {
	console.log('Building WMS layer:', layer_name, style);
	var bundle = 'basic';
	// check the layer name for the string 'maritime'
	// in which case we will need to specify the bundle
	// in the URL of our API request
	if (layer_name.indexOf('maritime') != -1) {
		bundle = 'maritime';
	}
	var url = 'https://api.wx.spire.com/ows/wms/?VERSION=1.3.0';
	url += '&SERVICE=WMS&REQUEST=GetMap&FORMAT=image/png&TRANSPARENT=true';
	url += '&WIDTH=1280&HEIGHT=1280&CRS=EPSG:3857&BBOX={bbox-epsg-3857}';
	url += '&LAYERS=' + layer_name;
	url += '&STYLES=' + style;
	url += '&TIME=' + time;
	url += '&bundle=' + bundle;
	url += '&spire-api-key=' + window.SPIRE_API_KEY;
	return url;
}

// add the WMS layer to the Mapbox basemap
function addLayerToMap(index, url) {
	var source_id = 'spire-wms-source-' + index;
	var layer_id = 'spire-wms-layer-' + index;
	window.map.addSource(source_id, {
		'type': 'raster',
		'tiles': [ url ],
		'tileSize': 256
	});
	window.map.addLayer({
		'id': layer_id,
		'type': 'raster',
		'source': source_id,
		'paint': {
			'raster-opacity': 0.8
		}
	});
	// keep track of the current layer in a global variable
	// in order to quickly reference it later
	window.Current_WMS_Layer[index] = window.map.getLayer(layer_id);
}

// replace TIME parameter in the WMS URL
function replaceTimeInURL(url, new_time) {
	// find location of TIME parameter in URL string
	var index = url.indexOf('TIME=');
	// get index of first character after `TIME=``
	index += 5;
	// get the current time string, which is always 20 characters
	var current_time = url.substr(index, 20);
	// replace the TIME= value with the new time
	var new_url = url.replace(current_time, new_time);
	return new_url;
}

// update the existing WMS layer with a new TIME parameter
function reconfigureLayerWithNewTime(index, time) {
	var source_id = 'spire-wms-source-' + index;
	var layer_id = 'spire-wms-layer-' + index;
	// get the current layer's URL
	var current_url = window.map.getSource(source_id)['tiles'][0];
	var new_url = replaceTimeInURL(current_url, time);
	// remove existing WMS layer
	window.map.removeLayer(layer_id);
	window.map.removeSource(source_id);
	// remove this layer index from the global WMS state
	delete window.Current_WMS_Layer[index];
	// add the WMS layer to the Mapbox basemap
	addLayerToMap(index, new_url);
}

// set the time for any instantiated WMS layer
function setWMSTime(time) {
	if (!time) {
		time = window.WMS_Animation_Current_Time;
	}
	console.log('WMS time being set to:', time);
	// change the UI time displays
	changeWMSTimeDisplay(time);
	// get the time array index of the new time
	var time_index = window.WMS_Animation_Times.indexOf(time);
	// set the UI slider position
	document.getElementById('wms_time_slider').value = time_index;
	// keep track of the current time array index
	window.WMS_Animation_Time_Index = time_index;
	// keep track of the full current time string
	window.WMS_Animation_Current_Time = time;
	// Q: is it dangerous to assume the same times exist for both layers?
	// A: yes, assumptions are dangerous.
	if (window.Current_WMS_Layer['0']) {
		reconfigureLayerWithNewTime(0, time);
	}
	if (window.Current_WMS_Layer['1']) {
		reconfigureLayerWithNewTime(1, time);
	}
}

// change the time string displayed in the UI
function changeWMSTimeDisplay(time) {
	document.getElementById('wms_time_display').innerHTML = time;
	document.getElementById('time_slider_display').innerHTML = time;
}

// stop the WMS animation
function stopWMS() {
	if (window.WMS_Animation !== null) {
		window.clearInterval(window.WMS_Animation);
		window.WMS_Animation = null;
	}
};

// start the WMS animation through available forecast times
function playWMS(index) {
	stopWMS();
	if (index) {
		window.WMS_Animation_Time_Index = index;
	}
	// var frameRate = 0.2; // 1 frame per 5 seconds
	// var frameRate = 0.5; // 1 frame per 2 seconds
	var frameRate = 0.1;
	window.WMS_Animation = window.setInterval(function() {
		var index = window.WMS_Animation_Time_Index;
		var times = window.WMS_Animation_Times;
		window.WMS_Animation_Current_Time = times[index];
		setWMSTime();
		if (index >= times.length - 1) {
			window.WMS_Animation_Time_Index = 0;
		} else {
			window.WMS_Animation_Time_Index = index + 1
		}
	}, 1000 / frameRate);
};

// set the opacity for a WMS layer
// (not actively used but useful in the JS console)
function setWMSOpacity(index, opacity) {
	var layer_id = 'spire-wms-layer-' + index;
	window.map.setPaintProperty(
		layer_id,
		'raster-opacity',
		opacity
	);
}
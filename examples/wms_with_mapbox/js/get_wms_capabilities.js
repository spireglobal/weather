// convert datetime text to milliseconds
function datestringToEpoch(ds) {
	var year = ds.substring(0, 4);
	var month = ds.substring(4, 6);
	var day = ds.substring(6, 8);
	var datestring = year + '-' + month + '-' + day;
	return new Date(datestring).getTime();
}

// get the full XML response of GetCapabilities
// which describes available layers, styles, and times
function getWMSCapabilities(bundle) {
	window.WMSRetrievalInitiated = true;
	console.log('Retrieving ' + bundle + ' WMS Capabilities...');
	var uri = 'https://api.wx.spire.com/ows/wms/?service=WMS&request=GetCapabilities&product=sof-d';
	uri += '&bundle=' + bundle;
	uri += '&spire-api-key=' + window.SPIRE_API_KEY;
	fetch(uri)
		.then(function(response) {
			if (response.status == 401) {
				document.getElementById('grayPageOverlay').style.display = 'block';
				document.getElementById('tokenPopup').style.display = 'block';
				// notify the user that the API response failed
				alert('API request failed for the Weather WMS API.\nPlease enter a valid API key or contact cx@spire.com')
			}
			// return the API response text
			// when it is received
			return response.text();
		})
		.then(function(str) {
			// parse the raw XML text into a JSON object
			var parsed = new WMSCapabilities(str).toJSON();
			return parsed;
		})
		.then(function(data) {
			console.log('Successfully retrieved ' + bundle + ' WMS Capabilities.');
			// keep track of this bundle's relevant capabilities in a global variable
			window.Full_WMS_XML[bundle] = {};
			// parse through the returned XML to get the layers broken down by date
			var capabilities = data['Capability'];
			var days = capabilities['Layer']['Layer'][0]['Layer'];
			// keep track of the most recent forecast
			// which we will use as the default
			var latest_date = {
				'text': '',
				'epoch': 0
			}
			// layers are first ordered by forecast date
			days.forEach(function(day) {
				// get the date text in this format: YYYYMMDD
				var dateText = day['Title'];
				var epochTime = datestringToEpoch(dateText);
				if (epochTime > latest_date['epoch']) {
					latest_date['text'] = dateText;
					latest_date['epoch'] = epochTime;
				}
				// keep track of each available date in our global object
				window.Full_WMS_XML[bundle][dateText] = {};
				// get the array of 4 forecast issuances
				var hours = day['Layer'];
				// iterate through the next level of layers (hours)
				hours.forEach(function(hour) {
					// get the hour text: 00, 06, 12, or 18
					var hourText = hour['Title'];
					// keep track of the date's available hours in our global object
					window.Full_WMS_XML[bundle][dateText][hourText] = {};
					// get the array of available weather variables
					var variables = hour['Layer'];
					// iterate through the next level of layers (data variables)
					variables.forEach(function(variable) {
						var name = variable['Name'];
						var displayName = variable['Title'];
						// get the time dimension objects
						var dimensions = variable['Dimension'];
						// skip if there's no time dimension
						if (dimensions == undefined) {
							return;
						}
						var times = [];
						// get the time string values
						dimensions.forEach(function(dimension) {
							// use the `time` dimension (not `reference_time`)
							if (dimension['name'] == 'time') {
								// convert comma-separated times from text to array
								times = dimension.values.split(',');
							}
						});
						// get the style options for this variable
						var styleOptions = variable['Style'];
						var stylesAndLegends = {};
						// get the name of each style for this variable
						styleOptions.forEach(function(style) {
							var styleName = style['Name'];
							var legend = style['LegendURL'];
							if (legend) {
								var legendURL = legend[0]['OnlineResource'];
								stylesAndLegends[styleName] = legendURL + '&spire-api-key=' + window.SPIRE_API_KEY;
							} else {
								stylesAndLegends[styleName] = 'none';
							}
						});
						// keep track of the available variables for this hour in our global object
						window.Full_WMS_XML[bundle][dateText][hourText][displayName] = {
							'name': name,
							'title': displayName,
							'styles': stylesAndLegends,
							'times': times,
							'bundle': bundle
						};
					});
				});
			});
			var latest_forecast = window.Full_WMS_XML[bundle][latest_date['text']];
			var issuance_times = Object.keys(latest_forecast);
			var forecast = null;
			// in the following set of conditionals,
			// we get the most recent issuance time of the latest forecast.
			// if there are not 50 or more available forecasted times,
			// data is still being processed,
			// so we move on to find the next complete forecast
			if (issuance_times.indexOf('18') != -1) {
				var latest = latest_forecast['18'];
				// get the array of available times for the first layer
				var times = Object.values(latest)[0]['times'];
				if (times.length >= 50) {
					// use the forecast issued at 18:00
					forecast = latest;
				}
			}
			if (forecast == null && issuance_times.indexOf('12') != -1) {
				var latest = latest_forecast['12'];
				// get the array of available times for the first layer
				var times = Object.values(latest)[0]['times'];
				if (times.length >= 50) {
					// use the forecast issued at 12:00
					forecast = latest;
				}
			}
			if (forecast == null && issuance_times.indexOf('06') != -1) {
				var latest = latest_forecast['06'];
				// get the array of available times for the first layer
				var times = Object.values(latest)[0]['times'];
				if (times.length >= 50) {
					// use the forecast issued at 06:00
					forecast = latest;
				}
			}
			if (forecast == null && issuance_times.indexOf('00') != -1) {
				var latest = latest_forecast['00'];
				// get the array of available times for the first layer
				var times = Object.values(latest)[0]['times'];
				// if (times.length >= 50) {
				// TODO: if there are less than 50 times then this is not a full forecast
				// and it might make sense to grab the last issuance from the previous date
				forecast = latest;
			}
			// add the WMS options to the global window.Latest_WMS object
			// which we will use to build the UI configurator
			var options = Object.keys(forecast);
			options.forEach(function(opt) {
				window.Latest_WMS[opt] = forecast[opt];
			});
			// check if 2 keys are present (current total bundles supported)
			// 1 for Basic and 1 for Maritime
			if (Object.keys(window.Full_WMS_XML).length == 2) {
				buildWMSConfigUI();
			}
		});
}

function buildWMSConfigUI() {
	console.log('Building WMS configuration UI.')
	var dropdownA = document.getElementById('wms_layer_select_0');
	var dropdownB = document.getElementById('wms_layer_select_1');
	// clear the dropdowns to get rid of 'Loading...' dropdown option
	dropdownA.innerHTML = null;
	dropdownB.innerHTML = null;
	// initiate both dropdowns with an option for none
	var null_option = document.createElement('OPTION');
	null_option.value = 'none';
	null_option.textContent = 'None';
	// initiate first dropdown with null option
	dropdownA.appendChild(null_option);
	// copy null option and initiate second dropdown
	dropdownB.appendChild(null_option.cloneNode(true));
	// build the dropdown contents
	var layer_titles = Object.keys(window.Latest_WMS);
	layer_titles.forEach(function(display_name) {
		var option = document.createElement('OPTION');
		option.value = display_name;
		option.textContent = display_name;
		// add option to first dropdown
		dropdownA.appendChild(option);
		// copy option and initiate second dropdown
		dropdownB.appendChild(option.cloneNode(true));
	});
	console.log('WMS configuration UI is ready.')
}

// Developer Note:
// It's possible to visualize forecasts other than the latest available by using the JS console.
// Check this to see what's available:
//	 	window.Full_WMS_XML
// Then run this to change the app config:
//		window.Latest_WMS = Object.assign({}, Full_WMS_XML['basic']['20200414']['12'], Full_WMS_XML['maritime']['20200414']['12']);

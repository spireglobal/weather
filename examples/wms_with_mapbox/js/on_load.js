// wait to execute the following code block until the page has fully loaded,
// ensuring that all HTML elements referenced here have already been created
window.onload = function() {
    // https://docs.mapbox.com/mapbox.js/example/v1.0.0/wms/
    // to make the basemap appear, you must
    // add your Mapbox access token from https://account.mapbox.com:
    mapboxgl.accessToken = null; // YOUR MAPBOX TOKEN
    // to make WMS metadata and layers appear, you must
    // add your Spire API key:
    window.SPIRE_API_KEY = null; // YOUR SPIRE API KEY
    // check to make sure above variables have been set
    if (mapboxgl.accessToken == null || window.SPIRE_API_KEY == null) {
        alert('Please add your Mapbox token and Spire API key \nto the top of the file: `js/on_load.js`');
    } else {
        // authentication variables are set properly,
        // so make the document body visible
        document.body.style.display = 'block';
    }
    // initialize the UI and global variables
    initialize();
};

function initialize() {
    // initialize variable for storing full WMS capabilities
    window.Full_WMS_XML = {};
    // initialize variable for storing the WMS options we will
    // make available to the user for configuration in the UI
    window.Latest_WMS = {};
    // initialize variable for storing the currently selected
    // WMS options (for both possible layers, indexed as '0' or '1')
    window.Current_WMS_Layer = {};
    // initialize quick lookup for available WMS times of current layers
    window.WMS_Animation_Times = [];
    // initialize variable for tracking the current index
    // of the WMS array of time values, used for animating WMS layers
    window.WMS_Animation_Time_Index = 0;
    // set a global variable for easy access of URL parameters
    // which are used for various configuration options
    window.urlParams = new URLSearchParams(window.location.search);

    // enable the WMS Configuration popup to be dragged around on the screen
    makeElementDraggable(document.getElementById('wmsPopup'));
    // enable the WMS legend popups to be dragged around on the screen
    makeElementDraggable(document.getElementById('legend_wms_0'));
    makeElementDraggable(document.getElementById('legend_wms_1'));
    // enable the WMS time popup to be dragged around on the screen
    makeElementDraggable(document.getElementById('wmsTimePopup'));

    // make async requests for the WMS capabilities
    // of the currently available bundles
    if (window.WMSRetrievalInitiated != true) {
        getWMSCapabilities('basic');
        getWMSCapabilities('maritime');
    }

    // create all necessary UI event handlers
    createEventHandlers()

    // create the Mapbox basemap
    window.map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v10',
        // style: 'mapbox://styles/mapbox/dark-v10',
        // style: 'mapbox://styles/mapbox/streets-v10',
        zoom: 2,
        center: [0, 20]
    });
}
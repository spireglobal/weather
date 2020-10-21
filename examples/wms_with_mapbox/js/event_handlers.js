function createEventHandlers() {
    // toggle popup for selecting a WMS layer
    document.getElementById('configureWMS').onclick = function() {
        if (document.getElementById('configureWMS').className != 'pressed') {
            document.getElementById('wmsPopup').style.display = 'block';
            document.getElementById('configureWMS').className = 'pressed';
        } else {
            document.getElementById('wmsPopup').style.display = 'none';
            document.getElementById('configureWMS').className = '';
        }
    };

    // toggle popup for WMS layer's legend image
    document.getElementById('show_legend_0').onclick = function() {
        if (document.getElementById('show_legend_0').className != 'pressed') {
            document.getElementById('show_legend_0').className = 'pressed';
            // make the legend image visible
            document.getElementById('legend_wms_0').style.display = 'inline-block';
        } else {
            document.getElementById('show_legend_0').className = '';
            // hide the legend image
            document.getElementById('legend_wms_0').style.display = 'none';
        }
    };
    // toggle popup for WMS layer's legend image
    document.getElementById('show_legend_1').onclick = function() {
        if (document.getElementById('show_legend_1').className != 'pressed') {
            document.getElementById('show_legend_1').className = 'pressed';
            // make the legend image visible
            document.getElementById('legend_wms_1').style.display = 'inline-block';
        } else {
            document.getElementById('show_legend_1').className = '';
            // hide the legend image
            document.getElementById('legend_wms_1').style.display = 'none';
        }
    };

    // click handler for for playing WMS time forward or stopping WMS time playback
    document.getElementById('wms_play_stop').onclick = function() {
        if (window.WMS_Animation == null) {
            // play WMS time forward
            // starting at the current time index
            playWMS();
            // switch to a 'pause' icon
            this.className = 'pause';
        } else {
            // stop WMS time playback
            // but do not change the time index
            stopWMS();
            // switch to a 'play' icon
            this.className = 'play';
        }
    };
    // handler for WMS time slider while it is moving
    document.getElementById('wms_time_slider').oninput = function() {
        if (window.WMS_Animation_Times.length > 0) {
            // use the integer value of the slider
            // to set the WMS time index
            var time = window.WMS_Animation_Times[this.value];
            // only change the time display, don't actually set the time
            changeWMSTimeDisplay(time);
        } else {
            // reset slider to starting position
            // if no WMS times are available
            this.value = 0;
        }
    };
    // handler for WMS time slider change (after mouse up)
    document.getElementById('wms_time_slider').onchange = function() {
        if (window.WMS_Animation_Times.length > 0) {
            // use the integer value of the slider
            // to set the WMS time index
            setWMSTime(window.WMS_Animation_Times[this.value]);
        } else {
            // reset slider to starting position
            // if no WMS times are available
            this.value = 0;
        }
    };
    // button for toggling map overlay time display
    document.getElementById('popout_time').onclick = function() {
        if (this.className != 'pressed') {
            this.className = 'pressed';
            // make the time popup visible
            document.getElementById('wmsTimePopup').style.display = 'block';
        } else {
            // hide the time popup
            this.className = '';
            document.getElementById('wmsTimePopup').style.display = 'none';
        }
    };

    // configure the styles dropdown based on the selected WMS layers
    function selectWMSAndPopulateStyles(layer_index) {
        var times = [];
        var style = null;
        var legend_url = null;
        var layer_selector = document.getElementById('wms_layer_select_' + layer_index);
        var layer_title = layer_selector.options[layer_selector.selectedIndex].value;
        if (layer_title == 'none') {
            // get the style selector
            var style_selector = document.getElementById('wms_style_select_' + layer_index);
            // clear the style selector contents
            style_selector.innerHTML = null;
            // make sure the style selector is no longer visible
            document.getElementById('wms_config_style_' + layer_index).style.display = 'none';
        } else {
            // get the times associated with the selected layer
            var times = window.Latest_WMS[layer_title]['times'];
            // get the styles associated with the selected layer
            var styles = window.Latest_WMS[layer_title]['styles'];
            // get the style selector
            var style_selector = document.getElementById('wms_style_select_' + layer_index);
            // clear the style selector contents
            style_selector.innerHTML = null;
            // make sure the style selector is visible
            document.getElementById('wms_config_style_' + layer_index).style.display = 'inline-block';
            // build the style dropdown contents
            var style_names = Object.keys(styles);
            style_names.forEach(function(name) {
                var option = document.createElement('OPTION');
                if (layer_index == '1' && name.indexOf('nearest') != -1) {
                    // don't set a value for the default layer style
                    // for the "overlay" WMS layer
                } else {
                    option.value = name;
                }
                option.textContent = name;
                // add option to dropdown
                style_selector.appendChild(option);
            });
            // select the last listed style by default for the second "overlay" dropdown
            // since it is meant to be a contour line on top of the first "base" dropdown
            if (layer_index == '1') {
                style_selector.selectedIndex = style_selector.options.length - 1;
            }
            style = style_selector.options[style_selector.selectedIndex].value;
            legend_url = styles[style];
        }
        var layer_name = 'none';
        if (window.Latest_WMS[layer_title] && window.Latest_WMS[layer_title]['name']) {
            layer_name = window.Latest_WMS[layer_title]['name'];
        }
        // add the WMS layer
        addWMSLayer(layer_name, style, layer_index, times, legend_url);
    }

    // configure the styles dropdown based on the selected WMS layers
    function selectNewStyleForWMS(layer_index) {
        // get selected layer 
        var layer_selector = document.getElementById('wms_layer_select_' + layer_index);
        var layer_title = layer_selector.options[layer_selector.selectedIndex].value;
        var layer_name = window.Latest_WMS[layer_title]['name'];
        // get the times associated with the selected layer
        var times = window.Latest_WMS[layer_title]['times'];
        // get selected style
        var style_selector = document.getElementById('wms_style_select_' + layer_index);
        var style = style = style_selector.options[style_selector.selectedIndex].value;
        var legend_url = window.Latest_WMS[layer_title]['styles'][style];
        // add the WMS layer
        addWMSLayer(layer_name, style, layer_index, times, legend_url);
    }

    // add the first WMS layer when a Layer is selected from the first Layer dropdown
    document.getElementById('wms_layer_select_0').onchange = function() {
        const layer_index = '0';
        selectWMSAndPopulateStyles(layer_index);
    };
    // add the first WMS layer when a Style is selected from the first Style dropdown
    document.getElementById('wms_style_select_0').onchange = function() {
        const layer_index = '0';
        selectNewStyleForWMS(layer_index);
    };

    // add the second WMS layer when a Layer is selected from the second Layer dropdown
    document.getElementById('wms_layer_select_1').onchange = function() {
        const layer_index = '1';
        selectWMSAndPopulateStyles(layer_index);
    };
    // add the second WMS layer when a Style is selected from the second Style dropdown
    document.getElementById('wms_style_select_1').onchange = function() {
        const layer_index = '1';
        selectNewStyleForWMS(layer_index);
    };

    // close the WMS popup when the X button is clicked
    document.getElementById('closeWMSPopup').onclick = function() {
        document.getElementById('wmsPopup').style.display = 'none';
        document.getElementById('configureWMS').className = '';
    };
}
var flowXL = flowXL || {};

flowXL.markerSelector = ( function() {
    function fetchJobDetails( jobID, onSuccess, onFailure ) {
        var r = new XMLHttpRequest();
        r.open("GET", "/api/1/jobs/" + jobID, false);
        r.onreadystatechange = function () {
            if (r.readyState != 4) {
                return;
            }
            
            if (r.status >= 400) {
                onFailure( "Failure to load job details for job " + jobID);
            } else {
                var details = JSON.parse(r.responseText);
                onSuccess(details);
            }
        };
        r.send();
    };

    function renderJobDetails( details, $el ) {
		// Clear the loading text
        $el.innerHTML = "";
		//*********************************************************************
		// Next, create the table of active markers
		//*********************************************************************
		var $table = new flowXL.markerTable(details, true);	
		// Build containers and place table inside
		var $table_container = document.createElement("div");
		$table_container.setAttribute('class','marker-table');
		var $table_container_panel = document.createElement("div");
		$table_container_panel.setAttribute('class', 'panel panel-default');
		var $table_container_panel_header = document.createElement("div");
		$table_container_panel_header.setAttribute('class', 'panel-heading');
		$table_container_panel_header.innerHTML = "<h3 class='panel-title'>Markers Used</h3>";
		
		// start putting things together
		$table_container_panel.appendChild($table_container_panel_header);
		$table_container_panel.appendChild($table);
        $table_container.appendChild($table_container_panel);
		$el.appendChild($table_container);
    }
    function init( jobID, containerName) {
        var $container = document.getElementById(containerName);
        $container.innerHTML = "<strong>Loading...</strong>";

        fetchJobDetails( jobID, function _onSuccess(details) { 
		this.details = details;
		renderJobDetails(details,$container)
		}, console.log);
    };

    return {
                init: init
    };
})();

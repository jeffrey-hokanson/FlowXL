var flowXL = flowXL || {};


flowXL.markerTable = ( function(details, showButtons) {
	// Takes a details object (following jobs/1 API) and a boolean
	// of wether or not to show buttons with this rendering
	// Returns a table element
	var $table = document.createElement("table");
   
	// if you have a problem with many, many files, it's probably because of this.
	//$table.width ="100%";
	
	var $header = document.createElement("tr");
	
	["File Name:"].concat(details.files).forEach( function _addHeader( headerName ) {
		var $columnHeader = document.createElement("th");
		$columnHeader.innerHTML = "<strong>"+headerName+"</strong>";
		$header.appendChild($columnHeader);
	});
	$table.appendChild($header);

	/*
	 * Start here to render columns!
	 */
	details.columns.forEach( function _addMarkerRows( marker ) {
		var $row = document.createElement("tr");
		
		// First row of the table
		var $button = document.createElement("td");
		// This is empty in this implementation, but buttons for selection show up in this row
		//$rowName.innerHTML = """<em>"+marker.name + "</em>";

		if (showButtons){
			// Now we check which kind of button we have 
			var buttonType = "";
			if (_.has(details.active, marker.name)){
				if (details.active[marker.name]){
					buttonType = 'minus';
				}
				else{
					buttonType = 'plus';
				}
			}
			// Only show plus/minus button on those rows where all files have that marker
			for (var i = 0; i < details.files.length; i++){
				if (_.indexOf(marker.files, details.files[i]) == -1){
					buttonType = '';
				}
			}	

			if (_.indexOf(['plus', 'minus'], buttonType) != -1){
				$button.innerHTML = "<button type='button' class='btn btn-default btn-sm'>"+
					"<span class='glyphicon glyphicon-" + buttonType + "'></span>" +
					"</button>";
			}
			else{
				$button.innerHTML ="<button type='button' class='btn btn-default btn-sm' disabled='true'>"+
					"<span class='glyphicon glyphicon-warning-sign'></span>" +
					"</button>";
			}
		}
		else{
			$button.innerHTML = "";
		}
		$row.appendChild($button);

		// Build out sequential rows in the table
		for (var i = 0; i < details.files.length; i++){
			var $rowEl = document.createElement("td");
			var elClass = ""
			$rowEl.innerHTML = marker.name;
			
			// See if the file has the marker labeled
			if (_.indexOf(marker.files, details.files[i]) != -1){
				elClass += "has-marker";
			}
			else {
				elClass += "not-has-marker";
			}
			// Next, see if the marker is active or not
			elClass +=" ";
			if (_.has(details.active, marker.name)){
				if (details.active[marker.name]){
					elClass += "active";
				}
				else{
					elClass += "inactive";
				}
			}
			else{
				elClass += "inactive";
			}

			$rowEl.setAttribute("class", elClass);
			$row.appendChild($rowEl);
		}


		// add the row to the table
		$table.appendChild($row);
	});
	return $table;
});


flowXL.jobDetails = ( function() {
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
		// First post the current job status
		//*********************************************************************

		// This container labels it for our purposes
		var $stat = document.createElement("div");
		$stat.setAttribute('class', 'job-status');
		$stat.innerHTML = "<div class='panel panel-default'>" +
			"<div class='panel-heading'> <h3 class='panel-title'> Job Status</h3></div>" +
			"<div class='panel-body'>" +  
			details.status + "</div></div>";
		$el.appendChild($stat);


		//*********************************************************************
		// Next, create the table of active markers
		//*********************************************************************
		var $table = flowXL.markerTable(details, false);	
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

        fetchJobDetails( jobID, function _onSuccess(details) { renderJobDetails(details,$container)}, console.log);
    };

    return {
                init: init
    };
})();

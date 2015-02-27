var flowXL = flowXL || {};


flowXL.MarkerTable = function(){
	this.details = "undefined";	// Will hold the details structure from jobs/1
	this.$table = document.createElement("table");
	//this.showButtons = true; // boolean; if the buttons should be rendered


	/* Grabs the details for a job and places them in the details structure
	 */
	this.loadJob = loadJob;
	function loadJob (jobID){
		self = this;
		//flowXL.MarkerTable.call(this);
		var r = new XMLHttpRequest();
		r.open("GET", "/api/1/jobs/" + jobID, false);
		r.onreadystatechange = function () {
			if (r.readyState != 4) {
				return;
			}
			
			if (r.status >= 400) {
				console.log( "Failure to load job details for job " + jobID);
			} else {
				self.details = JSON.parse(r.responseText);
				console.log('Got ' + r.responseText);
			}
		};
    r.send();
	};

	this.render = render;
	function render(showButtons){
		/* Takes a container where the table should be placed and renders the table there
		 * showButtons - (boolean) determines if the buttons should be shown
		 *
		 */

		var $table = this.$table;
		var details = this.details;

		// Nuke the current structure
		while ($table.firstChild){
			$table.removeChild($table.firstChild);
		}

		// Build top row of the table, containing the file names
		var $header = document.createElement("tr");
		["File Name:"].concat(details.files).forEach( function _addHeader( headerName ) {
			var $columnHeader = document.createElement("th");
			$columnHeader.innerHTML = "<strong>"+headerName+"</strong>";
			$header.appendChild($columnHeader);
		});
		$table.appendChild($header);

		// Now render each column
		details.columns.forEach( function _addMarkerRows( marker ) {
			var $row = document.createElement("tr");
			// First column of the table
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
		}); // End the loop over the table
	return $table;
	}

	this.toggleMarker = toggleMarker;
	function toggleMarker(newActive){
		// Takes a dictionary of marker and updates the details.active appropreately
		for (var key in newActive) {
			if (this.details.active.hasOwnProperty(key)){
				this.details.active[key] = newActive[key];
			}
			else{
				console.log("Tried to change state of invalid key" + key);
			}
		}
	};

};



flowXL.markerTable = ( function(details, showButtons) {
	/* Takes a details object (following jobs/1 API) and a boolean
	 * of wether or not to show buttons with this rendering
	 * Returns a table element
	 */
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



var flowXL = flowXL || {};


flowXL.MarkerTable = function(){
	this.details = "undefined";	// Will hold the details structure from jobs/1
	this.$table = document.createElement("table");

	/* Grabs the details for a job and places them in the details structure
	 */
	this.loadJob = loadJob;
	function loadJob (jobID){
		self = this;
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

        var buildButtonsForMarker = function( $row, marker ) {
			var $button = document.createElement("td");

			if (showButtons){
				// Now we check which kind of button we have 
				var buttonType = "";
				if (_.has(details.active, marker.name)){
					if (details.active[marker.name]){
						buttonType = 'check';
					}
					else{
						buttonType = 'unchecked';
					}
				}

				// Only show plus/minus button on those rows where all files have that marker
                details.files.forEach( function( file ) {
                    if ( !_.includes(marker.files, file) ) {
                        buttonType = '';
                    }
                });

                switch(buttonType) {
                    case "check": /* fall through */
                    case "unchecked" : 
                                    $button.innerHTML = "<button type='button' class='btn btn-default btn-sm' " + 
                                        "id='" + marker.name + "'" +
                                        ">"+
                                        "<span class='glyphicon glyphicon-" + buttonType + "'></span>" +
                                        "</button>";
                                    $button.addEventListener("click", (function (){
                                        var update = {};
                                        update[marker.name] = buttonType =="unchecked";
                                        this.toggleMarker(update);
                                        this.render(true);
                                        console.log("clicked " + marker.name);
                                    }).bind(this));
                                    break;
                    default: $button.innerHTML = "<button type='button' class='btn btn-default btn-sm' disabled='true'>"+
                        						 "<span class='glyphicon glyphicon-warning-sign'></span>" +
						                          "</button>";
                }
			}
			$row.appendChild($button);
        };

        // function that creates a row for a marker
        var renderMarkerRow = function ( marker ) {
			var $row = document.createElement("tr");

            buildButtonsForMarker.bind(this)( $row, marker);

            // First column of the table
            var addMarkersToRow = function ( $row, file ) {
				var $rowEl = document.createElement("td");
				var elClass = "";
				$rowEl.innerHTML = marker.name;
				
				// See if the file has the marker labeled
                elClass += (_.includes(marker.files,file))? "has-marker ":"not-has-marker ";

				// Next, see if the marker is active or not
                elClass += (details.active[marker.name])?"active":"inactive";

				$rowEl.setAttribute("class", elClass);
				$row.appendChild($rowEl);
            };

			// Build out sequential rows in the table
            details.files.forEach( addMarkersToRow.bind(this, $row) );

			// add the row to the table
			$table.appendChild($row);
        };

		// Now render each column
		details.markers.forEach( renderMarkerRow.bind(this) );
                
    	return $table;
	}

	this.toggleMarker = toggleMarker;
	
	function toggleMarker(newActive){
		// Takes a dictionary of marker and updates the details.active appropreately
        _.merge( this.details.active, newActive);
	};

};


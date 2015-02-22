var flowXL = flowXL || {};
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
        $el.innerHTML = "<strong>Loaded.</strong>";

        var $table = document.createElement("table");
       
        // if you have a problem with many, many files, it's probably because of this.
        $table.width ="100%";

        
        var $header = document.createElement("tr");
        
        ["Column"].concat(details.files).forEach( function _addHeader( headerName ) {
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
            
            // first, add marker name
            var $rowName = document.createElement("td");
            $rowName.innerHTML = "<em>"+marker.name + "</em>";
            $row.appendChild($rowName);

            // then, the hard part: add td items under the correct file column

            // add the row to the table
            $table.appendChild($row);
        });

        $el.appendChild($table);
        
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

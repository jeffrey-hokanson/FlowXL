var flowXL = flowXL || {};


flowXL.jobDetails = ( function() {
   
	this.mt = "";
	this.init = init;
	this.details = "";

	function init(jobID, jobDetailsName, markerTableName){

		var mt = new flowXL.MarkerTable();
		this.mt = mt;
		this.mt.loadJob(jobID);
		// We use MarkerTable to pull in the API details; this is a bit hackish
		this.details = this.mt.details;

		var $jobContainer = document.getElementById(jobDetailsName);
		var $markerContainer = document.getElementById(markerTableName);

		// Render the table of markers
		this.mt.$table = $markerContainer;
		this.mt.render(false);

		// Render the job information
		$jobContainer.innerHTML = this.details.status; 
	}

    return {
                init: init
    };
})();

var flowXL = flowXL || {};

flowXL.MarkerSelector = function() {

	this.mt = "";
	this.init  = init;
    
	function init( jobID, containerName) {
        // Loading message
		var $container = document.getElementById(containerName);
        $container.innerHTML = "<strong>Loading...</strong>";

		// Setup data for the marker table
		var mt = new flowXL.MarkerTable();
		this.mt = mt;
		this.mt.loadJob(jobID);
		$container.innerHTML = "";
		this.mt.render(true);
		$container.appendChild(this.mt.$table);
	}
};

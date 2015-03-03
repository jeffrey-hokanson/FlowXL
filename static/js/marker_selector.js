var flowXL = flowXL || {};

flowXL.MarkerSelector = function() {

	this.mt = "";
	this.init  = init;
    
	function init( jobID, containerName) {
        // Loading message
		var $container = document.getElementById(containerName);
        $container.innerHTML = "<strong>Loading...</strong>";
		var $table = document.createElement("table");

		// Setup data for the marker table
		var mt = new flowXL.MarkerTable();
		this.mt = mt;
		this.mt.init(jobID, $table, true);
		//this.mt.loadJob(jobID);
		this.mt.render(true);

		// Add the table
		$container.innerHTML = "";
		$container.appendChild(this.mt.$table);

	}
	this.bindSendActive = bindSendActive.bind(this);

	function bindSendActive(containerName){
		var $button = document.getElementById(containerName);
		$button.addEventListener("click", this.mt.sendActiveState);
	}
};

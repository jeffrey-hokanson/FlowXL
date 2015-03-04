var flowXL = flowXL || {};

flowXL.MarkerSelector = function() {

	this.mt = "";
	
	
	
	
	
	this.init  = init;
	
	function run(){
		// Submit the active markers
		this.mt.sendActiveState();
		// Check the email address
		var re =/\S+@\S+\.\S+/;
		var email = this.$emailContainer.value;
		console.log("Email: " + email);
		if (re.test(email)){
			console.log("Valid email");
			this.email = email;

			// Submit email address via API
			this.$alertContainer.innerHTML = "";
			this.sendEmailAddress();
			this.queueJob();
		}
		else{
			this.$alertContainer.innerHTML = "<div class='alert-danger' role='alert'> <strong> Oh snap!</strong> Try entering a valid email address and trying again</div>";	
			return "fail";
		}
		// Check number of files non-zero

		// Submit job 

	}
   


	this.sendEmailAddress = sendEmailAddress.bind(this);
	function sendEmailAddress(){
		var r = new XMLHttpRequest();
		r.open("PUT", '/api/1/jobs/' + this.jobID + '/email', false);
		r.setRequestHeader('Content-type','application/json; charset=utf-8');		
		var data = {email: this.email};
		console.log(data);
		r.send(JSON.stringify(data));
	}

	this.queueJob = queueJob.bind(this);

	function queueJob(){
		var r = new XMLHttpRequest();
		r.open("POST", '/api/1/jobs/' + this.jobID + '/queue', false);
		//r.setRequestHeader('Content-type','application/json; charset=utf-8');		
		//var data = {email: this.email};
		//console.log(data);
		//r.send(JSON.stringify(data));
		r.send();
	}



	function init( jobID, tableContainerName, emailContainerName, runContainerName, alertContainerName) {
        // Loading message
		var $container = document.getElementById(tableContainerName);
        $container.innerHTML = "<strong>Loading...</strong>";
		var $table = document.createElement("table");

		// Setup data for the marker table
		var mt = new flowXL.MarkerTable();
		this.mt = mt;
		this.mt.init(jobID, $table, true);
		this.jobID = jobID;
		//this.mt.loadJob(jobID);
		this.mt.render(true);

		// Add the table
		$container.innerHTML = "";
		$container.appendChild(this.mt.$table);

		// Setup callbacks for the run button
		
		this.$runButton = document.getElementById(runContainerName);
		this.$emailContainer = document.getElementById(emailContainerName);
		this.$alertContainer = document.getElementById(alertContainerName);

		this.$runButton.addEventListener("click", run.bind(this));
	}
	
	
	
	this.bindSendActive = bindSendActive.bind(this);
	function bindSendActive(containerName){
		var $button = document.getElementById(containerName);
		$button.addEventListener("click", this.mt.sendActiveState);
	}
};

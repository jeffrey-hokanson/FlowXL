#! /usr/bin/python

from flask import Flask, Response, jsonify, render_template, json, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
import os
from os.path import join
import simplejson

from datetime import datetime

# For ServerSent Events
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from lib import fcs

from lib.upload_file import uploadfile

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['fcs'])
IGNORED_FILES = set(['.gitignore'])


# Setup of the database
dbfile = join(os.path.dirname(os.path.realpath(__file__)), 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + dbfile
db = SQLAlchemy(app)

# Generic setup
app.config['DATA_PATH'] = join(os.path.dirname(os.path.realpath(__file__)), 'data')


# List of subscribers 
SUBSCRIPTIONS = []


################################################################################
# Database Configuration 
################################################################################

class Active(db.Model):
	""" Holds list of active markers per job
	"""
	__tablename__ = 'active'
	__table_args__ = (
		db.PrimaryKeyConstraint('job_id', 'marker', name = 'job_id_and_marker'),
	)
	
	job_id = db.Column(db.BigInteger, index = True)
	marker = db.Column(db.Text)
	status = db.Column(db.Boolean)

	def __init__(self, job_id, marker, status):
		# TODO Add sanity checks
		self.job_id = job_id
		self.marker = marker
		self.status = status

class Files(db.Model):
	__tablename__ = 'files'
	__table_args__ = (
			db.PrimaryKeyConstraint('job_id', 'filename', name = 'job_id_and_filename'),
		)

	job_id = db.Column(db.BigInteger, index = True)
	filename = db.Column(db.Text, index = True)
	
	def __init__(self, job_id, filename):
		self.job_id = job_id
		self.filename = filename

class Markers(db.Model):
	__tablename__ = 'markers'
	__table_args__ = (
			db.PrimaryKeyConstraint('job_id', 'filename', 'marker', name = 'job_id_and_filename_and_marker'),
		)
	
	job_id = db.Column(db.BigInteger, index = True)
	filename = db.Column(db.Text, index = True)
	marker = db.Column(db.Text, index = True)
	
	def __init__(self, job_id, filename, marker):
		self.job_id = job_id
		self.filename = filename
		self.marker = marker

class Jobs(db.Model):
	__tablename__ = 'jobs'
	__table_args__ = (
			db.PrimaryKeyConstraint('id'),
		)
	id = db.Column(db.BigInteger, index = True)
	perplexity  = db.Column(db.Float)
	email = db.Column(db.Text)
	first_access = db.Column(db.DateTime)
	ip = db.Column(db.Text)
	status = db.Column(db.Text)
	progress = db.Column(db.Float)
	def __init__(self, id, perplexity = 20, email = None, first_access = None, ip = None, status = 'uploading', progress = 0.):
		self.id = id
		self.perplexity = perplexity
		self.email = email


		if first_access is None:
			first_access = datetime.now()
		self.first_access = first_access
		self.ip = ip
		self.status = status
		self.progress = progress



################################################################################
# Server Sent Events Class 
################################################################################

# Follows: http://flask.pocoo.org/snippets/116/
class ServerSentEvent(object):
	""" Class for transimmitting server sent events to the webpage
	"""

	def __init__(self, data):
		self.data = data
		self.event = None
		self.id = None
		self.desc_map = {
				self.data : "data",
				self.event : "event",
				self.id : "id"
		}

	def encode(self):
		if not self.data:
			return ""
		lines = ["%s: %s" %(v, k)
				for k, v in self.desc_map.iteritems() if k]
		return "%s\n\n" % "\n".join(lines)


################################################################################
# Web Pages 
################################################################################
@app.route("/")
def hello():
	ip = request.remote_addr
	job_id = get_job(ip)
	print "Requesting IP address: " + str(ip)
	return redirect('/{}'.format(job_id))

@app.route("/<int:job_id>/")
def upload_page(job_id):
	return render_template('upload_page.html', job_id = job_id)


@app.route("/test/selector", methods=["GET"])
def test_selector():
    job_id = 1
    return render_template("marker_selector.html", job_id=job_id)


@app.route("/jobs/<int:job_id>", methods=["GET"])
def display_job_details(job_id):
    return render_template("job_details.html", job_id=job_id)



################################################################################
# Helper Functions
################################################################################

def get_job(ip):
	"""Return the job_id of either a new job or the job currently used by 
	the requesting IP address
	"""
	
	# See if we have an open job for the current IP address:
	job = db.session.query(Jobs).filter(Jobs.ip == ip, Jobs.status == 'uploading').first()
	print job
	if job:
		return job.id
	else:
		max_id = db.session.query(db.func.max(Jobs.id)).scalar()
		if max_id is not None:
			new_id = max_id + 1
		else:
			new_id = 1
		
		new_job = Jobs(new_id, ip = ip)
		db.session.merge(new_job)
		db.session.commit()
		return new_id

def publish(job_id, message):
	""" Sends message to the subscribers
	"""

	def notify():
		for sub in SUBSCRIPTIONS[:]:
			sub.put(message)
	
	gevent.spawn(notify)
	return "OK"

def allowed_file(filename):
	""" Helper function that returns true if we can read the provided file type
	"""
	allowed_extensions = ['fcs']
	return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_base_path(job_id):
	""" Helper function that returns the folder on disk where files are stored.
	"""
	return join(app.config['DATA_PATH'], '%09d' % (job_id,))


def make_col_entry( name, files ):
    return { "name":name, "files":files }

def make_job_details_dict( files, status, markers, active):
	return { "files":files, "status":status, "markers":markers, "active": active} 


def import_file(job_id, filename):
	""" Adds database entires corresponding to the FCS file
	"""
	base_path = get_base_path(job_id)
	filepath = join(base_path, filename)
	if True:
		(data, metadata, analysis, meta_analysis) = fcs.read(filepath, only_header = True)
		# First, add the file to the database
		row = Files(job_id, filename)
		db.session.merge(row)
		db.session.commit()

		nparameters = int(metadata['$PAR'])
		marker_names = [ metadata.get('$P{:d}N'.format(j), None) for j in range(1,nparameters+1) ]
		marker_snames = [ metadata.get('$P{:d}S'.format(j), None) for j in range(1,nparameters+1) ]

		# Now add the markers, picking the best of either S or N
		for n,s in zip(marker_names, marker_snames):
			if s is not None:
				marker = s
			else:
				marker = n
			row = Markers(job_id, filename, marker)
			db.session.merge(row)
			db.session.commit()
	else:
		#TODO Should return an error back to the user if we cannot process the file
		pass

def delete_file(job_id, filename):
	""" Removes a file from the database

	"""
	for file in db.session.query(Files).filter(Files.job_id == job_id, Files.filename == filename).all():
		db.session.delete(file)
		db.session.commit()
	
	for marker in db.session.query(Markers).filter(Markers.job_id == job_id, Markers.filename == filename).all():
		db.session.delete(marker)
		db.session.commit()

def get_active(job_id):
	"""Return a dictionary listing which markers are active
	"""
	# Generate default state of markers 
	r = db.session.query(Markers).filter(Markers.job_id == job_id).all()
	all_markers = list(set([m.marker for m in r]))
	active = {}	
	total_files = db.session.query(Files).filter(Files.job_id == job_id).count()
	for marker in all_markers:
		total_for_marker = db.session.query(Markers).filter(Markers.job_id == job_id, Markers.marker == marker).count()
		active[marker] = ( total_files == total_for_marker )
		# Now set state in database
		#a = Active(job_id, marker, active[marker])
		#db.session.merge(a)
		#db.session.commit()
	
	# Load the state of markers already in the database
	r = db.session.query(Active).filter(Active.job_id == job_id).all()
	for a in r:
		active[a.marker] = a.status
	
	for marker in active:
		a = Active(job_id, marker, active[marker])
		db.session.merge(a)
		db.session.commit()
	
	
	return active

def get_status(job_id):
	"""Returns the status of a job
	"""
	r = db.session.query(Jobs).filter(Jobs.id == job_id).first()
	return r.status

################################################################################
# API
################################################################################

@app.route('/api/1/jobs/<int:job_id>/subscribe')
def subscribe(job_id):
	""" Location where ServerSentEvents are sent from.

		Follows: http://flask.pocoo.org/snippets/116/
	"""
	def gen():
		q = Queue()
		SUBSCRIPTIONS.append(q)
		try:
			while True:
				result = q.get()
				ev = ServerSentEvent(str(result))
				yield ev.encode()
		except GeneratorExit:
			SUBSCRIPTIONS.remove(q)
	
	return Response(gen(), mimetype='text/event-stream')



@app.route("/api/1/jobs/<int:job_id>/upload", methods = ['GET','POST'])
def upload(job_id):
	""" Provides API for reading/uploading the files on the disk
	"""
	base_path = get_base_path(job_id)

	# Make the directory for holding the data if necessary
	if not os.path.exists(base_path):
		os.makedirs(base_path)

	if request.method == 'POST':
		file = request.files['file']
		if file:
			filename = secure_filename(file.filename)
			mimetype = file.content_type

			if not allowed_file(filename):
				result = uploadfile(name=filename, type=mimetype, size=0, not_allowed_msg="Filetype not allowed", job_id = job_id)
			else:
				# save file to disk
				filepath = join(base_path, filename)
				file.save(filepath)
				
				# get file size after saving
				size = os.path.getsize(filepath)

                # return json for js call back
				result = uploadfile(name=filename, type=mimetype, size=size, job_id = job_id)
			
				# process file
				import_file(job_id, filename)

				# Send message about a new file
				publish(job_id, "update: new file")
			return simplejson.dumps({"files": [result.get_file()]})
	
	if request.method == 'GET':
		# get all file in ./data directory
		files = [ f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path,f)) and f not in IGNORED_FILES ]    
		file_display = []

		for f in files:
			size = os.path.getsize(os.path.join(base_path, f))
			file_saved = uploadfile(name=f, size=size, job_id = job_id)
			file_display.append(file_saved.get_file())

		return simplejson.dumps({"files": file_display})

	return redirect(url_for('/'))

@app.route("/api/1/jobs/<int:job_id>/delete/<string:filename>", methods=['DELETE'])
def delete(job_id, filename):
	base_path = get_base_path(job_id)
	file_path = os.path.join(base_path, filename)
    #file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

	if os.path.exists(file_path):
		try:
			os.remove(file_path)
			delete_file(job_id, filename)
			publish(job_id, "update: delete file")
			return simplejson.dumps({filename: 'True'})
		except:
			return simplejson.dumps({filename: 'False'})

@app.route("/api/1/jobs/<int:job_id>/data/<string:filename>", methods=['GET'])
def get_file(job_id, filename):
	base_path = get_base_path(job_id)
	return send_from_directory(base_path, filename=filename)

@app.route("/api/1/jobs/<int:job_id>", methods=["GET"])
def api_handle_job_details(job_id):

	files = db.session.query(Files).filter(Files.job_id == job_id).all()
	filenames = [ f.filename for f in files]
	markers = db.session.query(Markers).filter(Markers.job_id == job_id).all()
	# Get the list of unqiue markers
	unique_markers = list(set([m.marker for m in markers]))

	marker_table = []
	
	for marker in unique_markers:
		files_for_marker = db.session.query(Markers).filter(Markers.job_id == job_id, Markers.marker == marker).all()
		files_for_marker = [ f.filename for f in files_for_marker]
		marker_table.append(make_col_entry(marker, files_for_marker))
		
#		# If the marker is contained in every file, set it to active
#		active[marker] = (len(files_for_marker) == len(filenames))

	active = get_active(job_id)
	status = get_status(job_id)
	return jsonify( make_job_details_dict( filenames, status, marker_table, active) )



@app.route("/api/1/jobs/<int:job_id>/active", methods = ["PUT"])
def api_handle_job_active(job_id):
	""" Handles mapping the return state of active markers into the database
	"""
	# TODO: This should only be allowed when the job is in a certain state (i.e., 
	# you should not be able to change markers while the t-SNE job is running.
	if request.method == 'PUT':
		if request.headers['Content-Type'].lower() == 'application/json; charset=utf-8':
			active = request.json
			for marker in active:
				print "Job %d recieved marker %s : %s" % (job_id, marker, str(active[marker]))
				row = Active(job_id, marker, active[marker])
				db.session.merge(row)
				db.session.commit()
		
		#print json.dumps(request.json)
		return 'OK'
	
#	if request.method == 'GET':
#		active = get_active(job_id)
#		return simplejson.dumps(active)	

@app.route("/api/1/jobs/<int:job_id>/email", methods = ["PUT"])
def api_handle_job_email(job_id):
	""" Takes a string as input, maps it to the email address
	"""

	if request.method == 'PUT':
		if request.headers['Content-Type'].lower() == 'application/json; charset=utf-8':
			print request.json
			email = request.json['email']
			job = db.session.query(Jobs).filter(Jobs.id == job_id).first()
			job.email = email
			db.session.merge(job)
			db.session.commit()
			print "Added Email"
			return "OK"
	print "failed to add email"
	return "Fail"

@app.route("/api/1/jobs/<int:job_id>/queue", methods = ["POST"])
def api_handle_job_queue(job_id):
	"""When called, this pushes job_id onto the queue.
	"""
	
	if request.method == "POST":
		job = db.session.query(Jobs).filter(Jobs.id == job_id).first()
		job.status = 'queued'
		db.session.merge(job)
		db.session.commit()
	
		print "%d job queued" % (job_id,)
		return "OK"
	return "FAILED"

if __name__ == "__main__":

	# Running in debug mode introduces ability interactively debug
	# i.e., if file saved, reloads server.
	# Note, debug mode is ___UNSAFE___
	#app.run(debug = True)
	app.debug = True
	server = WSGIServer(("",5000), app)
	server.serve_forever()


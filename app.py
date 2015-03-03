from flask import Flask, jsonify, render_template, json, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
import os
from os.path import join
import simplejson

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


class Active(db.Model):
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

#class Marker(db.Model):
#	__tablename__ = 'marker'


@app.route("/")
def hello():
	job_id = 1
	return redirect('/{}'.format(job_id))

@app.route("/<int:job_id>/")
def upload_page(job_id):
	return render_template('upload_page.html', job_id = job_id)


def make_col_entry( name, files ):
    return { "name":name, "files":files }

def make_job_details_dict( files, status, markers, active):
	return { "files":files, "status":status, "markers":markers, "active": active} 


################################################################################
# API
################################################################################

def allowed_file(filename):
	""" Helper function that returns true if we can read the provided file type
	"""
	allowed_extensions = ['fcs']
	return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route("/api/1/jobs/<int:job_id>/upload", methods = ['GET','POST'])
def upload(job_id):
	""" Provides API for reading/uploading the files on the disk
	"""
	base_path = join(app.config['DATA_PATH'], '%09d' % (job_id,))

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
			
			return simplejson.dumps({"files": [result.get_file()]})
	
	if request.method == 'GET':
		# get all file in ./data directory
		files = [ f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path,f)) and f not in IGNORED_FILES ]    
		file_display = []
		print files

		for f in files:
			size = os.path.getsize(os.path.join(base_path, f))
			file_saved = uploadfile(name=f, size=size, job_id = job_id)
			file_display.append(file_saved.get_file())

		return simplejson.dumps({"files": file_display})

	return redirect(url_for('/'))

@app.route("/api/1/jobs/<int:job_id>/delete/<string:filename>", methods=['DELETE'])
def delete(job_id, filename):
	base_path = join(app.config['DATA_PATH'], '%09d' % (job_id,))
	file_path = os.path.join(base_path, filename)
    #file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

	if os.path.exists(file_path):
		try:
			os.remove(file_path)
			return simplejson.dumps({filename: 'True'})
		except:
			return simplejson.dumps({filename: 'False'})

@app.route("/api/1/jobs/<int:job_id>/data/<string:filename>", methods=['GET'])
def get_file(job_id, filename):
	base_path = join(app.config['DATA_PATH'], '%09d' % (job_id,))
	return send_from_directory(base_path, filename=filename)

@app.route("/api/1/jobs/<int:job_id>", methods=["GET"])
def api_handle_job_details(job_id):
    files = [ "I01-4078770-Unstained-IrOnly_cells_found.fcs", "I02-4078770-PB-Baseline_cells_found.fcs","I03-4078770-BM-Baseline_cells_found.fcs"]
    status = "queued"
    markers = [ make_col_entry('CD8a', files), 
				make_col_entry( "CD45", files), 
				make_col_entry( "CD133", [files[0]]), 
				make_col_entry( "CD123", [files[1]])
			]
    active = {"CD8a": False, "CD45": True, "CD133": False, "CD123": False}
    return jsonify( make_job_details_dict( files, status, markers, active) )


@app.route("/test/selector", methods=["GET"])
def test_selector():
    job_id = 1
    return render_template("marker_selector.html", job_id=job_id)

@app.route("/api/1/jobs/<int:job_id>/active", methods = ["PUT"])
def api_handle_job_active(job_id):
	""" Handles mapping the return state of active markers into the database
	"""
	# TODO: This should only be allowed when the job is in a certain state (i.e., 
	# you should not be able to change markers while the t-SNE job is running.
	if request.headers['Content-Type'].lower() == 'application/json; charset=utf-8':
		active = request.json
		for marker in active:
			print job_id, marker, active[marker]
			row = Active(job_id, marker, active[marker])
			db.session.merge(row)
			db.session.commit()

		#TODO: This dummy code should be replaced to update the database
		print json.dumps(request.json)
	return 'OK'

@app.route("/jobs/<int:job_id>", methods=["GET"])
def display_job_details(job_id):
    return render_template("job_details.html", job_id=job_id)

if __name__ == "__main__":

	# Running in debug mode introduces ability interactively debug
	# i.e., if file saved, reloads server.
	# Note, debug mode is ___UNSAFE___
	app.run(debug = True)


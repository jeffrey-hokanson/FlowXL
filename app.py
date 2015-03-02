from flask import Flask, jsonify, render_template, json, request
from flask.ext.sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)



# Setup of the database
dbfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + dbfile
db = SQLAlchemy(app)

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
	return render_template('main.html')

def make_col_entry( name, files ):
    return { "name":name, "files":files }

def make_job_details_dict( files, status, markers, active):
	return { "files":files, "status":status, "markers":markers, "active": active} 


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


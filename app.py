from flask import Flask, jsonify, render_template
import simplejson

app = Flask(__name__)

@app.route("/")
def hello():
	return render_template('main.html')

def make_col_entry( name, files ):
    return { "name":name, "files":files }

def make_job_details_dict( files, status, columns ):
    return { "files":files, "status":status, "columns":columns } 


@app.route("/api/1/jobs/<int:job_id>", methods=["GET"])
def api_handle_job_details(job_id):
    files = [ "file1.bbq", "file2.wtf", "file3.lol"]
    status = "queued"
    columns = [ make_col_entry( "col1", files), make_col_entry( "col2", [files[0]]), make_col_entry( "col3", [files[1]]) ]

    return jsonify( make_job_details_dict( files, status, columns) )

@app.route("/jobs/<int:job_id>", methods=["GET"])
def display_job_details(job_id):
    return render_template("job_details.html", job_id=job_id)

if __name__ == "__main__":

	# Running in debug mode introduces ability interactively debug
	# i.e., if file saved, reloads server.
	# Note, debug mode is ___UNSAFE___
	app.run(debug = True)


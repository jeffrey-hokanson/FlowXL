from flask import Flask, jsonify, render_template
app = Flask(__name__)

@app.route("/")
def hello():
	return render_template('main.html')

def make_col_entry( name, files ):
    return { "name":name, "files":files }


@app.route("/api/1/jobs/<int:job_id>", methods=["GET"])
def api_handle_job_details(job_id):
    files = [ "file1.bbq", "file2.wtf", "file3.lol"]
    status = "queued"
    columns = [ make_col_entry( "col1", files), make_col_entry( "col2", [files[0]]), make_col_entry( "col3", [files[1]]) ]

    return jsonify( files=files, status=status, columns=columns )


if __name__ == "__main__":

	# Running in debug mode introduces ability interactively debug
	# i.e., if file saved, reloads server.
	# Note, debug mode is ___UNSAFE___
	app.run(debug = True)


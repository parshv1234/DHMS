from app import create_app
from flask import Flask,  redirect,render_template,request, session, url_for,jsonify,flash 

# Create the Flask app using the factory function
app = create_app()

@app.route('/')
def Home():
	return render_template('./index.html')

@app.errorhandler(403)
def unauthorized_access(e):
    flash("You are not authorized to access this page.", "danger")
    return render_template('auth/403.html'), 403

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

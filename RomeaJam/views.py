from RomeaJam import app #, render_template

@app.route('/')
@app.route('/index')
def index():
    return 'Hello World!'


#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404

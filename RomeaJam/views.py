from RomeaJam import app

@app.route('/')
def index():
        return 'Hello World!'


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

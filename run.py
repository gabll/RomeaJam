#!venv/bin/python
from RomeaJam import app, scheduler
scheduler.start()
app.run(host= '0.0.0.0', debug=True, use_reloader=False)

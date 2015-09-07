import flask
import uuid
import datetime

app = flask.Flask(__name__)


@app.route('/widget/<widget_id>', methods=['GET'])
def get_widget(widget_id):
    now = datetime.datetime.utcnow().isoformat()
    return flask.jsonify({'widget_id': widget_id, 'date_created': now})


@app.route('/add', methods=['POST'])
def add_widget():
    content = flask.request.get_json()
    widget_id = content.get('widget_id', None)
    try:
        val = uuid.UUID(widget_id, version=1)
    except (ValueError, TypeError):
        flask.abort(403)

    if str(val) != widget_id:
        flask.abort(403)
    else:
        now = datetime.datetime.utcnow().isoformat()
        return flask.jsonify({'widget_id': widget_id, 'date_created': now}), \
            201, {'Location': '{0}'.format(
                flask.url_for('get_widget', widget_id=widget_id))}

if __name__ == '__main__':
    app.run(debug=True)

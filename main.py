from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_bootstrap import Bootstrap
from flask_dotenv import DotEnv
from functools import wraps

import helper

app = Flask(__name__)
Bootstrap(app)
env = DotEnv()
env.init_app(app)
env.eval(keys={
    'DEBUG': int,
    'MAX_CONTENT_LENGTH': int
});
helper.set_app(app)

def give_it_a_try(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except helper.RESTException, e:
            response = e.response
            return response.content, response.status_code
    return decorated_function

class Bucket(object):
    def __init__(self, name, get_link, delete_link, *args, **kwargs):
        self.name = name
        self.get_link = get_link
        self.delete_link = delete_link

class Object(Bucket):
    def __init__(self, *args, **kwargs):
        super(Object, self).__init__(*args, **kwargs)

# lists all buckets
@app.route('/', methods=['GET'])
@give_it_a_try
def get_all_buckets():
    buckets = helper.get_buckets()
    rendered_buckets = []
    for bucket in buckets:
        rendered_bucket = Bucket(name=bucket,
                                 get_link=url_for('get_all_objects',
                                                  bucket_name=bucket),
                                 delete_link=url_for('delete_bucket',
                                                     bucket_name=bucket))
        rendered_buckets.append(rendered_bucket)
    return render_template('index.html',
                           buckets=rendered_buckets,
                           create_bucket_link=url_for('create_bucket'))

# lists all objects in a bucket
@app.route('/<bucket_name>', methods=['GET'])
@give_it_a_try
def get_all_objects(bucket_name):
    objects = helper.get_objects(bucket_name)
    rendered_objects = []
    for _object in objects:
        rendered_object = Object(name=_object,
                                 delete_link=url_for('delete_object',
                                                     bucket_name=bucket_name,
                                                     object_name=_object),
                                 get_link=url_for('get_object',
                                                  bucket_name=bucket_name,
                                                  object_name=_object))
        rendered_objects.append(rendered_object)
    buckets = helper.get_buckets()
    bucket_names = []
    for bucket in buckets:
        if bucket != bucket_name:
            bucket_names.append(bucket)
    return render_template('bucket.html',
                           bucket_name=bucket_name,
                           bucket_names=bucket_names,
                           objects=rendered_objects,
                           create_object_link=url_for('create_object'),
                           copy_object_link=url_for('copy_object'))

# delete a bucket
@app.route('/delete-bucket/<bucket_name>', methods=['GET'])
@give_it_a_try
def delete_bucket(bucket_name):
    helper.delete_bucket(bucket_name)
    return redirect(url_for('get_all_buckets'))

# create a bucket
@app.route('/create-bucket', methods=['POST'])
@give_it_a_try
def create_bucket():
    bucket_name = request.form.get('bucket')
    helper.put_bucket(bucket_name)
    return redirect(url_for('get_all_buckets'))

# download a file
@app.route('/<bucket_name>/<object_name>', methods=['GET'])
@give_it_a_try
def get_object(bucket_name, object_name):
    res = helper.get_object(bucket_name, object_name)
    return res, 200, \
           {'Content-Disposition': 'attachment; filename=%s' % object_name}

# delete object
@app.route('/delete-object/<bucket_name>/<object_name>', methods=['GET'])
@give_it_a_try
def delete_object(bucket_name, object_name):
    helper.delete_object(bucket_name, object_name)
    return redirect(url_for('get_all_objects', bucket_name=bucket_name))

# create object
@app.route('/create-object', methods=['POST'])
@give_it_a_try
def create_object():
    bucket_name = request.form.get('bucket')
    object_name = request.form.get('object')
    if 'up_object' not in request.files \
            or request.files['up_object'].filename == '':
        return 'No file selected', 400
    uploaded_file = request.files['up_object']
    if object_name == '' or type(object_name) == 'undefined':
        object_name = uploaded_file.filename
    buf = uploaded_file.read()
    helper.put_object(bucket_name, object_name, buf)
    return redirect(url_for('get_all_objects', bucket_name=bucket_name))

# copy object between buckets
@app.route('/copy-object', methods=['POST'])
@give_it_a_try
def copy_object():
    source_bucket = request.form.get('source_bucket')
    source_object = request.form.get('source_object')
    destination_bucket = request.form.get('destination_bucket')
    destination_object = request.form.get('destination_object')
    if type(destination_object) == 'undefined' or destination_object == '':
        destination_object = source_object
    helper.copy_object(source_bucket, source_object, destination_bucket, destination_object)
    return redirect(url_for('get_all_objects', bucket_name=source_bucket))

if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])

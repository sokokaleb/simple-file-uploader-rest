import requests

app = None

class RESTException(Exception):
    def __init__(self, response, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        self.response = response


def set_app(used_app):
    global app
    app = used_app

def get_buckets():
    response = requests.get(app.config['ENDPOINT_URL'])
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.json()

def get_objects(bucket_name):
    response = requests.get('{}/{}'.format(app.config['ENDPOINT_URL'],
        bucket_name))
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.json()

def get_object(bucket_name, object_name):
    response = requests.get('{}/{}/{}'.format(app.config['ENDPOINT_URL'],
        bucket_name,
        object_name))
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.content

def delete_bucket(bucket_name):
    response = requests.delete('{}/{}'.format(app.config['ENDPOINT_URL'],
        bucket_name))
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.content

def delete_object(bucket_name, object_name):
    response = requests.delete('{}/{}/{}'.format(app.config['ENDPOINT_URL'],
        bucket_name,
        object_name))
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.content

def put_bucket(bucket_name):
    response = requests.put('{}/{}'.format(app.config['ENDPOINT_URL'],
        bucket_name))
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.content

def put_object(bucket_name, object_name, data):
    response = requests.put('{}/{}/{}'.format(app.config['ENDPOINT_URL'],
        bucket_name,
        object_name),
        data=data)
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.content

def copy_object(source_bucket, source_object, destination_bucket, destination_object=None):
    if destination_object is None:
        destination_object = source_object
    response = requests.request('COPY', '{}/{}/{}/{}/{}'.format(app.config['ENDPOINT_URL'],
        source_bucket,
        source_object,
        destination_bucket,
        destination_object))
    if response.status_code != 200:
        raise RESTException(response=response)
    return response.content

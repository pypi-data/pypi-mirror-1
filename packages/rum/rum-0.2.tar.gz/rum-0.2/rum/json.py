from turbojson.jsonify import jsonify
from rum import fields, app, Query

@jsonify.when((fields.Field,))
def jsonify_field(obj):
    attrs = dict(obj.attrs)
    attrs['type'] = obj.field_type
    return attrs

@jsonify.when((fields.Relation,))
def jsonify_relation(obj):
    attrs = dict(obj.attrs)
    attrs['other'] = app.url_for(attrs['other'], action='_meta')
    attrs['type'] = obj.field_type
    return attrs

@jsonify.when((Query,))
def jsonify_query(obj):
    d = obj.as_dict()
    d['count'] = obj.count
    return d

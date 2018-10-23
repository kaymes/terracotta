"""server/datasets.py

Flask route to handle /datasets calls.
"""

from flask import request, jsonify
from marshmallow import Schema, fields, validate, INCLUDE

from terracotta.server.flask_api import convert_exceptions, metadata_api, spec


class DatasetOptionSchema(Schema):
    class Meta:
        unknown = INCLUDE

    # placeholder values to document keys
    key1 = fields.String(example='value1', description='Value of key1', dump_only=True)
    key2 = fields.String(example='value2', description='Value of key2', dump_only=True)

    # real options
    limit = fields.Integer(
        description='Maximum number of returned datasets per page', missing=100,
        validate=validate.Range(min=0)
    )
    page = fields.Integer(
        missing=0, description='Current dataset page', validate=validate.Range(min=0)
    )


class DatasetSchema(Schema):
    datasets = fields.List(
        fields.Dict(values=fields.String(example='value1'),
                    keys=fields.String(example='key1')),
        required=True,
        description='Array containing all available key combinations'
    )
    limit = fields.Integer(description='Maximum number of returned items', required=True)
    page = fields.Integer(description='Current page', required=True)


@metadata_api.route('/datasets', methods=['GET'])
@convert_exceptions
def get_datasets() -> str:
    """Get all available key combinations
    ---
    get:
        summary: /datasets
        description:
            Get keys of all available datasets that match given key constraint.
            Constraints may be combined freely. Returns all known datasets if no query parameters
            are given.
        parameters:
          - in: query
            schema: DatasetOptionSchema
        responses:
            200:
                description: All available key combinations
                schema:
                    type: array
                    items: DatasetSchema
            400:
                description: Query parameters contain unrecognized keys
    """
    from terracotta.handlers.datasets import datasets
    option_schema = DatasetOptionSchema()
    options = option_schema.load(request.args)

    limit = options.pop('limit')
    page = options.pop('page')
    keys = options or None

    payload = {
        'datasets': datasets(keys, page=page, limit=limit),
        'limit': limit,
        'page': page
    }

    schema = DatasetSchema()
    return jsonify(schema.load(payload))


spec.definition('Dataset', schema=DatasetSchema)

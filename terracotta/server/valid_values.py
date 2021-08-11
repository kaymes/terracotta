"""server/datasets.py

Flask route to handle /datasets calls.
"""

from typing import Any, Dict, List, Union
from flask import request, jsonify, Response
from marshmallow import Schema, fields, validate, INCLUDE, post_load
import re

from terracotta.server.flask_api import METADATA_API


class KeyValueOptionSchema(Schema):
    class Meta:
        unknown = INCLUDE

    # placeholder values to document keys
    key1 = fields.String(example='value1', description='Value of key1', dump_only=True)
    key2 = fields.String(example='value2', description='Value of key2', dump_only=True)

    @post_load
    def list_items(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Union[str, List[str]]]:
        # Create lists of values supplied as stringified lists
        for key, value in data.items():
            if isinstance(value, str) and re.match(r'^\[.*\]$', value):
                data[key] = value[1:-1].split(',')
        return data


@METADATA_API.route('/valid_values', methods=['GET'])
def get_valid_values() -> Response:
    """Get all valid values combinations (possibly when given a value for some keys)
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
    from terracotta.handlers.valid_values import valid_values
    option_schema = KeyValueOptionSchema()
    options = option_schema.load(request.args)

    keys = options or None

    payload = {
        'valid_values': valid_values(keys)
    }

    return jsonify(payload)

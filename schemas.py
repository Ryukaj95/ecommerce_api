from marshmallow import Schema, fields
from marshmallow_jsonschema import JSONSchema


class OrderSchema(Schema):
    uuid = fields.UUID()
    total_price = fields.Decimal()
    user = fields.Nested(UserSchema)


class OrderItemSchema(Schema):
    order = fields.Nested(UserSchema)
    item = fields.Nested(ItemSchema)
    quantity = fields.Decimal()
    subtotal = fields.Decimal()

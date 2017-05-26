from marshmallow import Schema, fields


class OrderSchema(Schema):
    total_price = fields.Integer()
    user = fields.Nested(UserSchema)
    items = fields.Nested(OrderItemSchema)


class OrderItemSchema(Schema):
    item = fields.String()
    quantity = fields.Integer()
    subtotal = fields.Integer()

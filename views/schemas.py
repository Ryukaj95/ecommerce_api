from marshmallow import Schema, fields


class OrderSchema(Schema):
    uuid = fields.UUID()
    total_price = fields.Integer()
    user = fields.Nested(UserSchema)
    items = fields.Nested(OrderItemSchema)


class OrderItemSchema(Schema):
    order = fields.UUID()
    item = fields.String()
    quantity = fields.Integer()
    subtotal = fields.Integer()

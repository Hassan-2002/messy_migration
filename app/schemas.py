from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=False, allow_none=True)

class UserCreateSchema(UserSchema):
    password = fields.Str(required=True, validate=validate.Length(min=6))

    class Meta:
        fields = ("name", "password", "email")
        ordered = True

class UserUpdateSchema(UserSchema):
    name = fields.Str(required=False, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=False, allow_none=True)
    password = fields.Str(required=False, validate=validate.Length(min=6))

class LoginSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))

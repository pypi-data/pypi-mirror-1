from sqlalchemy import types

import uuid
class UuidType(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, engine):
        return str(value)

    def process_result_value(self, value, engine):
        # return uuid.UUID(value)
        return value

    def copy(self):
        return UuidType(self.impl.length)

    @classmethod
    def default(self):
        # return uuid.uuid4()
        return str(uuid.uuid4())


import simplejson
class JsonType(types.TypeDecorator):
    '''Store data as JSON serializing on save and unserializing on use.
    '''
    impl = types.UnicodeText

    def process_bind_param(self, value, engine):
        # None or {}
        if not value:
            return None
        else:
            # ensure_ascii=False => allow unicode but still need to convert
            return unicode(simplejson.dumps(value, ensure_ascii=False))

    def process_result_value(self, value, engine):
        if value is None:
            return None
        else:
            return simplejson.loads(value)

    def copy(self):
        return JsonType(self.impl.length)


import swiss.date as date_mod
class FlexiDateType(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, engine):
        if value is None: # TODO: empty string?
            return None
        else:
            return str(date_mod.parse(value))

    def process_result_value(self, value, engine):
        return value

    def copy(self):
        return self.__class__(self.impl.length)


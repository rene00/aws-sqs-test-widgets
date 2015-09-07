import base64
import json


class BaseMsgError(Exception):
    pass


class BaseMsg():

    @staticmethod
    def get_body(msg):
        return json.loads(base64.b64decode(msg.get_body()))

    @staticmethod
    def get_std_response(obj):
        return {'MessageId': obj.id,
                'WidgetId': obj.widget_id}

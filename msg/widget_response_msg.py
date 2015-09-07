from base_msg import BaseMsg, BaseMsgError
import requests
import json


class WidgetResponseMsgError(BaseMsgError):
    pass


class WidgetResponseMsg(BaseMsg):

    def __init__(self, msg, sqs, **kwargs):
        self.msg = msg
        self.sqs = sqs

        self.id = self.msg.id
        self.queue = self.msg.queue
        self.body = BaseMsg().get_body(self.msg)
        self.widget_id = self.body.get('WidgetId', None)
        self.widget_maker_url = kwargs.get('widget_maker_url',
                                           'http://localhost:5000/add')

    def __repr__(self):
        return '<WidgetResponseMsg widget_id:{0.widget_id}>'.format(self)

    def process(self):
        data = {'widget_id': self.widget_id}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        widget = requests.post(self.widget_maker_url, data=json.dumps(data),
                               headers=headers)
        try:
            widget.raise_for_status()
        except requests.exceptions.HTTPError:
            raise
        else:
            return widget

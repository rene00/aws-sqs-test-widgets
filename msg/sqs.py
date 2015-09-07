from boto.exception import NoAuthHandlerFound
from boto.sqs.message import RawMessage
import base64
import boto.sqs
import json
import time


SQS_AUTH_RETRIES = 5
NUM_MSGS = 10
WAIT_TIME = 20
VISIBILITY_TIMEOUT = 2


class SQSAuthError(Exception):
    pass


class SQS():

    def __init__(self, region=None):
        self.region = region
        self.conn = None

    def connect(self, region=None):
        """ Connect into SQS. """
        if self.region and not region:
            region = self.region
        else:
            self.region = region

        tries = 0
        while self.conn is None and tries < SQS_AUTH_RETRIES:
            tries += 1
            try:
                self.conn = boto.sqs.connect_to_region(region)
            except NoAuthHandlerFound as e:
                if str(e)[:37] != "No handler was ready to authenticate.":
                    raise
                time.sleep(1)

        if self.conn is None:
            raise SQSAuthError("could not authenticate to SQS")

        return self.conn

    def get_msgs(self, queue, visibility_timeout=VISIBILITY_TIMEOUT,
                 num_messages=NUM_MSGS, wait_time_seconds=WAIT_TIME,
                 attributes=['All']):
        """ Get SQS messages. """
        q = self.conn.lookup(queue)
        q.set_message_class(RawMessage)
        return q.get_messages(num_messages=num_messages,
                              visibility_timeout=visibility_timeout,
                              wait_time_seconds=wait_time_seconds,
                              attributes=attributes)

    def write_msg(self, queue, msg):
        """ Write SQS message as JSON. """
        m = RawMessage()
        m.set_body(base64.b64encode(json.dumps(msg)))
        q = self.conn.lookup(queue)
        msg_sent = q.write(m)
        print("Sent Msg; queue={0}, msg={1.id}".format(queue, msg_sent))
        return msg_sent

    def delete_msg(self, queue, msg):
        """ Delete a SQS message. """
        q = self.conn.lookup(queue)
        msg_del = q.delete_message(msg)
        print("Deleted Msg; queue={0}, msg={1.id}".format(queue, msg))
        return msg_del

    def update_msg(self, queue, orig_msg, new_msg):
        """ Update a SQS message. """
        status = self.write_msg(self, queue, new_msg)
        self.delete_msg(queue, self.conn, orig_msg)
        print("Updating Msg; queue={0}, orig_msg={1.id}, new_msg={2.id}"
              .format(queue, orig_msg, new_msg))
        return status

    def manage_failed_request(self, queue, msg, visibility_timeout=30,
                              receive_count_limit=3):
        """Handle a failed request that has come through SQS.

        If a msg has been read less than receive_count, set the visibility
        timeout. Once receive_count has been reached, delete the message.
        """

        receive_count = int(
            msg.attributes.get('ApproximateReceiveCount', 0))

        if receive_count >= receive_count_limit or receive_count == 0:
            print("Failed message reached, deleting; receive_count={0},"
                  " receive_count_limit={1}, msg={2.id}".format(
                      receive_count, receive_count_limit, msg))
            return self.delete_msg(queue, msg)
        else:
            print("Message Failed, setting visibility_timeout; "
                  "visibility_timeout={0}, msg={1.id}, receive_count={2}, "
                  "receive_count_limit={3}".format(visibility_timeout, msg,
                                                   receive_count,
                                                   receive_count_limit))
            return msg.change_visibility(visibility_timeout)

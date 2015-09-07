import argparse
from msg import SQS, WidgetResponseMsg
import sys
import time
import requests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', dest='region', default=None, required=None,
                        help='AWS region for SQS')
    parser.add_argument('--sqs-request-queue', dest='sqs_request_queue',
                        default='WidgetRequestQueue', required=False,
                        help='SQS Request Queue')
    parser.add_argument('--sqs-response-queue', dest='sqs_response_queue',
                        default='WidgetResponseQueue', required=False,
                        help='SQS Response Queue')
    parser.add_argument('--sleep', dest='sleep', default=2, required=False,
                        help='Seconds to sleep between responses')
    return parser.parse_args()


def main():
    args = parse_args()

    while True:
        sqs = SQS()
        sqs.connect(args.region)
        for _msg in sqs.get_msgs(args.sqs_request_queue):

            msg = WidgetResponseMsg(_msg, sqs)

            print("Received Msg; msg={0.id}, body={0.body}".format(msg))

            # Create response message.
            msg_resp = msg.get_std_response(msg)

            try:
                widget = msg.process()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    # Our widget id is most likely not UUID v1.
                    print("Widget maker rejected widget; msg={0.id}, "
                          "status_code={1.status_code}".format(msg,
                                                               e.response))
                    sqs.delete_msg(args.sqs_request_queue, _msg)
                else:
                    print("Widget maker failed to make widget; msg={0.id} "
                          "status_code={1.status_code}".format(msg,
                                                               e.response))
                    sqs.manage_failed_request(args.sqs_request_queue, _msg)
                continue
            except requests.exceptions.ConnectionError:
                print("Widget maker is down; msg={0.id}".format(msg))
                sqs.manage_failed_request(args.sqs_request_queue, _msg)
                continue
            else:
                print("Widget created; msg={0.id}, body={1.content}"
                      .format(msg, widget))
                msg_resp.update({"Status": "OK"})

            # Send Response Message.
            sqs.write_msg(args.sqs_response_queue, msg_resp)

            # Delete Request Message.
            sqs.delete_msg(args.sqs_request_queue, _msg)

        time.sleep(float(args.sleep))


if __name__ == "__main__":
    sys.exit(main())

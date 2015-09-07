import argparse
from msg import SQS
import sys
import uuid


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', dest='region', default=None, required=True,
                        help='AWS region for SQS')
    parser.add_argument('--widget-id', dest='widget_id',
                        default=str(uuid.uuid1()), required=False,
                        help='AWS region for SQS')
    parser.add_argument('--sqs-request-queue', dest='sqs_request_queue',
                        default='WidgetRequestQueue', required=False,
                        help='SQS Request Queue')
    return parser.parse_args()


def main():
    args = parse_args()
    msg_resq = {'WidgetId': args.widget_id}
    sqs = SQS(args.region)
    sqs.connect()
    sqs.write_msg(args.sqs_request_queue, msg_resq)


if __name__ == '__main__':
    sys.exit(main())

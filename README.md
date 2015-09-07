AWS SQS Test Widgets
====================

This is a proof of concept which consists of

 -  A [producer](widget_producer.py) which is tasked with submitting new
    requests that create widgets.

 - A [consumer](widget_consumer.py) which takes the new request and
    POSTs it to a widget maker web app.

 - A [widget maker web app](widget_maker.py) which takes the POST
   request, validates the request and creates the widget.


The [consumer](widget_response.py) will make use of SQS's [visibility
timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/AboutVT.html) feature and the [ApproximateReceiveCount](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html) attribute to manage invalid requests or resend a request if the [widget maker web app](widget_marker.py) is down.


Setup
----


Build the virtualenv.

```
make
```

Create the SQS queues WidgetRequestQueue & WidgetResponseQueue. The
example below uses the ap-southeast-2 region.

Run
---

Run the widget maker.

```
$ venv/bin/python widget_maker.py
```

Run the consumer.

```
$ venv/bin/python widget_consumer.py --region=ap-southeast-2
```

Generate a new widget request using a randomly generated widget id.

```
$ venv/bin/python widget_producer.py --region=ap-southeast-2
```

Generate a new widget request with a specific valid widget id.
```
$ venv/bin/python widget_producer.py --region=ap-southeast-2 \
    --widget-id=31f37378-54f4-11e5-ad75-3c970e65f731
```

Generate a new widget request with an invalid widget-id.
```
$ venv/bin/python widget_producer.py --region=ap-southeast-2 \
    --widget-id=this_is_not_a_valid_widget_id
```

To see the use of [visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/AboutVT.html) and the
[ApproximateReceiveCount](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html) attribute in action, stop widget_maker.py and submit a new request.


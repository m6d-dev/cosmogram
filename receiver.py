import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.exchange_declare(exchange="fanout_msg", exchange_type="fanout")

result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange="fanout_msg", queue=queue_name)


def callback(ch, method, properties, body):
    print(f" [x] {body}")


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

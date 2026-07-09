import pika
import os
from pika.exceptions import AMQPConnectionError


class RabbitMQTopicConsumer:
    """
    Clase para consumir mensajes de un Exchange de tipo 'topic' en RabbitMQ.
    Gestiona la conexión y la suscripción de forma robusta.
    """

    def __init__(self, exchange_name: str, binding_key: str):
        self.exchange_name = exchange_name
        self.binding_key = binding_key
        self.queue_name = None
        self._connection = None
        self._channel = None

        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASS", "guest")
        credentials = pika.PlainCredentials(user, password)
        self.connection_params = pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials
        )

    def _connect(self):
        """Establece la conexión, el canal y la suscripción."""
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = pika.BlockingConnection(self.connection_params)
                self._channel = self._connection.channel()
                self._channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic', durable=True)

                # Declara una cola exclusiva para este consumidor. RabbitMQ le dará un nombre único.
                result = self._channel.queue_declare(queue='', exclusive=True)
                self.queue_name = result.method.queue

                # Vincula la cola al exchange con la binding key para recibir mensajes.
                self._channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.binding_key)
            except AMQPConnectionError as e:
                print(f"Error al conectar con RabbitMQ: {e}")
                raise

    def start_consuming(self, on_message_callback):
        """Inicia el bucle de consumo de mensajes."""
        self._connect()
        print(f" [*] Mailer esperando por eventos con binding_key '{self.binding_key}'. Para salir presiona CTRL+C")

        def callback_wrapper(ch, method, properties, body):
            on_message_callback(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self._channel.basic_consume(queue=self.queue_name, on_message_callback=callback_wrapper)
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            print("\nConsumo interrumpido por el usuario.")
        finally:
            self.close()

    def close(self):
        """Cierra la conexión si está abierta."""
        if self._connection and self._connection.is_open:
            self._connection.close()

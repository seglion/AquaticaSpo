import pika
import json
import os
from pika.exceptions import AMQPConnectionError


class RabbitMQTopicPublisher:
    """
    Clase para publicar mensajes en un Exchange de tipo 'topic' en RabbitMQ.
    Gestiona la conexión de forma eficiente y se puede usar como un context manager.
    """

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        # El nombre del servicio 'rabbitmq' en docker-compose es la URL
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")

        # Leer credenciales desde las variables de entorno para la autenticación
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASS", "guest")
        credentials = pika.PlainCredentials(user, password)

        self.connection_params = pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials
        )
        self._connection = None
        self._channel = None

    def _connect(self):
        """Establece la conexión y el canal si no existen o están cerrados."""
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = pika.BlockingConnection(self.connection_params)
                self._channel = self._connection.channel()
                # Declaramos el exchange de tipo 'topic'
                self._channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic', durable=True)
            except AMQPConnectionError as e:
                print(f"Error al conectar con RabbitMQ en '{self.connection_params.host}': {e}")
                raise

    def send_message(self, routing_key: str, message_body: dict):
        """Envía un mensaje a la cola especificada."""
        self._connect()  # Asegura que la conexión está activa
        self._channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=json.dumps(message_body)
        )
        print(f" [x] Enviado mensaje con routing_key '{routing_key}': {message_body}")

    def close(self):
        """Cierra la conexión si está abierta."""
        if self._connection and self._connection.is_open:
            self._connection.close()

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
import pika
from abc import ABC, abstractmethod


class AbstractPublisher(ABC):
    def __init__(self, host: str):
        self.host: str = host
        self.exchange: str = None
        self.queue: str = None
        self.bind: str = None
        self.routing_key: str = None

    def connect(self):
        self.connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()

    @abstractmethod
    def declare_exchange(self):
        """Объявление exchange, зависит от типа обменника"""
        pass

    @abstractmethod
    def declare_queue(self):
        """Объявление queue, зависит от exchange"""
        pass

    @abstractmethod
    def declare_bind(self):
        """Объявление bind, зависит от exchange, queue"""
        pass

    @abstractmethod
    def publish_message(self, message: str):
        """Публикация сообщения, конкретная реализация в наследнике"""
        pass

    def close(self):
        if self.connection:
            self.connection.close()

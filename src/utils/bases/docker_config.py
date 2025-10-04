from src.apps.core.consts import GHCR_HOST
from docker.errors import DockerException
from contextlib import contextmanager
from docker import DockerClient
import docker


class DockerConfig:
    def __init__(self):
        self._client = None

    def get_client(self) -> DockerClient:
        """Получить клиента Docker, с lazy инициализацией."""
        if self._client is None:
            try:
                self._client = docker.from_env()
                # Тест подключения
                self._client.ping()
            except DockerException as e:
                raise RuntimeError(f"Не удалось подключиться к Docker: {e}")
        return self._client

    def is_available(self) -> bool:
        """Проверить доступность сокета Docker."""
        try:
            self.get_client().ping()
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Закрыть клиент явно."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def login_to_ghcr(self, username: str, token: str) -> None:
        client = self.get_client()
        try:
            client.login(username=username, password=token, registry=GHCR_HOST)
        except DockerException as e:
            raise RuntimeError(f"Логин в ghcr.io прозошла ошибка: {e}")

    def push_image(self, tag: str, username: str, token: str) -> None:
        client = self.get_client()
        try:
            client.login(username=username, password=token, registry=GHCR_HOST)
            for line in client.images.push(tag, stream=True, decode=True):
                print(line)
        except DockerException as e:
            raise RuntimeError(f"Ошибка при пуше образа: {e}")

    @contextmanager
    def client_context(self):
        """Контекстный менеджер для безопасного использования клиента."""
        client = self.get_client()
        try:
            yield client
        finally:
            self.close()

import socket
import logging
from setting import DISTRIBUTOR_SERVER_PORT
import click
from my_types import Game

@click.option('server_port')
def server_port(server_port):
    return server_port


log_format = '[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s'
logging.basicConfig(filename="log.log", level=logging.DEBUG, format=log_format)
logger = logging.getLogger(f'game_server_{server_port()}')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
sock.bind(('', server_port()))  # связываем сокет с портом, где он будет ожидать сообщения
sock.listen(2)  # указываем сколько может сокет принимать соединений
print('Server is running, please, press ctrl+c to stop')

while True:
    connection, address = sock.accept()  # начинаем принимать соединения
    logger.debug('connected:', address)  # выводим информацию о подключении
    data = connection.recv(1024)  # принимаем данные от клиента, по 1024 байт
    logger.debug(f'Data: {str(data)}')

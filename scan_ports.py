import nmap
import telegram
import asyncio
import datetime
import socket


# Конфигурация
token = "111111111111"
chat_id = "1111111111"
target_hosts = ["80.78.240.10"]  # Список целевых хостов для сканирования
scanning_interval = 300  # Интервал сканирования в секундах

previous_open_ports = {}

async def send_telegram_message(message):
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)

async def get_service_name(port, protocol):
    try:
        service = socket.getservbyport(port, protocol)
        return service
    except OSError:
        return ""

async def scan_ports():
    for target_host in target_hosts:
        # Создаем объект nmap и запускаем сканирование портов
        nm = nmap.PortScanner()
        nm.scan(hosts=target_host, arguments='-Pn')

        # Получаем открытые порты TCP и UDP
        open_ports = {}
        for host in nm.all_hosts():
            if 'tcp' in nm[host]:
                for port in nm[host]['tcp']:
                    if nm[host]['tcp'][port]['state'] == 'open':
                        service = await get_service_name(port, 'tcp')
                        open_ports[port] = ('tcp', service)
            if 'udp' in nm[host]:
                for port in nm[host]['udp']:
                    if nm[host]['udp'][port]['state'] == 'open':
                        service = await get_service_name(port, 'udp')
                        open_ports[port] = ('udp', service)

        # Проверяем изменения в открытых портах
        new_open_ports = {k: v for k, v in open_ports.items() if k not in previous_open_ports.get(target_host, {})}
        closed_ports = {k: v for k, v in previous_open_ports.get(target_host, {}).items() if k not in open_ports}

        # Формируем сообщение для отправки в Telegram
        message = ""
        if new_open_ports:
            message += f"Новые порты, открытые на {target_host}:\n"
            for port, (protocol, service) in new_open_ports.items():
                message += f"Порт {port} ({protocol}) - {service}\n"
        if closed_ports:
            message += f"Закрытые порты на {target_host}:\n"
            for port, (protocol, service) in closed_ports.items():
                message += f"Порт {port} ({protocol}) - {service}\n"

        # Если есть изменения в портах, отправляем сообщение
        if message:
            await send_telegram_message(message)

        # Обновляем предыдущие открытые порты
        previous_open_ports[target_host] = open_ports

    # Запускаем следующее сканирование через указанный интервал времени
    await asyncio.sleep(scanning_interval)
    await scan_ports()

# Запускаем сканирование портов
asyncio.run(scan_ports())

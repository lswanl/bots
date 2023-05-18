import time
import subprocess
import requests

TOKEN = 'koten_id'
CHANNEL_ID = 'chat_id'
IP_ADDRESSES = 'ip_address' # если нужно сканировать несколько адресов то дожны выглядеть так ['ip_address_1', 'ip_address_2', и тд]

previous_ports = {}

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': CHANNEL_ID,
        'text': message
    }
    requests.post(url, json=payload)

def scan_ports(ip_address):
    global previous_ports

    command = f'nmap -Pn -p- {ip_address}'
    output = subprocess.check_output(command, shell=True, text=True)
    open_ports = {}

    for line in output.splitlines():
        if 'open' in line:
            port = line.split('/')[0]
            open_ports[port] = True

    new_open_ports = [port for port in open_ports if port not in previous_ports.get(ip_address, {})]
    new_closed_ports = [port for port in previous_ports.get(ip_address, {}) if port not in open_ports]

    if new_open_ports:
        message = f'Новые открытые порты на {ip_address}:\n' + ', '.join(new_open_ports)
        send_telegram_message(message)

    if new_closed_ports:
        message = f'Новые закрытые порты на {ip_address}:\n' + ', '.join(new_closed_ports)
        send_telegram_message(message)

    previous_ports[ip_address] = open_ports

while True:
    for ip_address in IP_ADDRESSES:
        scan_ports(ip_address)
    time.sleep(30)

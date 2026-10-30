"""NEXUS RADAR — diagnóstico e descoberta básica da rede local."""

import concurrent.futures
import datetime
import ipaddress
import os
import shutil
import socket
import subprocess


CYAN = "\033[96m"
DIM = "\033[90m"
RESET = "\033[0m"


def _clear():
    os.system("clear")


def _header():
    _clear()
    print(CYAN + r"""
╔══════════════════════════════════════════════════════╗
║                    NEXUS RADAR                       ║
║             NETWORK DIAGNOSTICS CENTER               ║
╚══════════════════════════════════════════════════════╝
""" + RESET)


def _local_ip():
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("1.1.1.1", 80))
        return probe.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def _gateway():
    try:
        with open("/proc/net/route", encoding="utf-8") as route_file:
            next(route_file)
            for line in route_file:
                fields = line.split()
                if len(fields) > 3 and fields[1] == "00000000":
                    return socket.inet_ntoa(
                        bytes.fromhex(fields[2])[::-1]
                    )
    except (OSError, ValueError, StopIteration):
        pass
    return "Indisponível"


def _pause():
    try:
        input("\nPressione Enter para voltar...")
    except EOFError:
        pass


def _dns():
    host = input("Domínio ou hostname > ").strip()
    if not host:
        return
    try:
        results = sorted({
            item[4][0]
            for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        })
        print("\nEndereços encontrados:")
        for address in results:
            print("  • " + address)
    except socket.gaierror as error:
        print(f"\nFalha na consulta DNS: {error}")


def _ping():
    host = input("Host ou IP para testar > ").strip()
    if not host:
        return
    ping = shutil.which("ping")
    if not ping:
        print("Comando ping não encontrado.")
        return
    print()
    try:
        result = subprocess.run(
            [ping, "-c", "4", "-W", "2", host],
            check=False
        )
        if result.returncode:
            print("\nO destino não respondeu aos testes.")
    except OSError as error:
        print(f"Não foi possível executar ping: {error}")


def _scan():
    local = _local_ip()
    try:
        network = ipaddress.ip_network(local + "/24", strict=False)
    except ValueError:
        print("Não foi possível determinar a rede local.")
        return

    if not network.is_private:
        print("A faixa detectada não é uma rede privada. Varredura cancelada.")
        return

    print(f"Rede detectada: {network}")
    print("A descoberta testa conexões TCP comuns somente na rede local.")
    print("Use apenas em uma rede sua ou com autorização.")
    answer = input("Continuar? [s/N] > ").strip().lower()
    if answer not in ("s", "sim"):
        print("Varredura cancelada.")
        return

    ports = (80, 443, 22, 5555)
    found = []
    hosts = list(network.hosts())
    print(f"\nVerificando {len(hosts)} endereços...")

    def check(address):
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.22)
            try:
                if sock.connect_ex((str(address), port)) == 0:
                    return str(address), port
            finally:
                sock.close()
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
        for result in pool.map(check, hosts):
            if result:
                found.append(result)

    if not found:
        print("\nNenhum dispositivo com as portas testadas respondeu.")
        print("Isso não significa que não existam outros dispositivos.")
        return

    devices = sorted({address for address, _ in found},
                     key=lambda value: int(ipaddress.ip_address(value)))
    print(f"\nPossíveis dispositivos encontrados: {len(devices)}")
    for address in devices:
        ports_found = ", ".join(
            str(port) for ip, port in found if ip == address
        )
        try:
            name = socket.gethostbyaddr(address)[0]
        except (socket.herror, socket.gaierror):
            name = "nome não identificado"
        print(f"  {address:<16} {name}  portas: {ports_found}")


def run(cfg=None):
    while True:
        _header()
        print(" [1] Informações da rede")
        print(" [2] Consulta DNS")
        print(" [3] Teste de ping")
        print(" [4] Descobrir dispositivos da rede local")
        print(" [0] Voltar")
        choice = input("\nRadar > ").strip()

        if choice == "1":
            _header()
            print("DIAGNÓSTICO DA REDE\n")
            print("Data/hora: " + datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
            print("Hostname: " + socket.gethostname())
            print("IP local: " + _local_ip())
            print("Gateway: " + _gateway())
            print("DNS configurado:")
            try:
                with open("/etc/resolv.conf", encoding="utf-8") as dns_file:
                    servers = [
                        line.split()[1] for line in dns_file
                        if line.strip().startswith("nameserver") and len(line.split()) > 1
                    ]
                print("\n".join("  • " + server for server in servers) or "  Não identificado")
            except OSError:
                print("  Não foi possível ler /etc/resolv.conf")
            _pause()
        elif choice == "2":
            _header()
            _dns()
            _pause()
        elif choice == "3":
            _header()
            _ping()
            _pause()
        elif choice == "4":
            _header()
            _scan()
            _pause()
        elif choice == "0":
            return

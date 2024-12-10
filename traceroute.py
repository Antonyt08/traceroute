import socket
import struct
import time
import sys
import matplotlib.pyplot as plt
from datetime import datetime


def calculate_checksum(data):
    checksum = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        checksum += (data[i] << 8) + data[i + 1]
    if n:
        checksum += data[-1]
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += checksum >> 16
    return ~checksum & 0xffff


def create_icmp_packet(identifier, sequence_number, is_ipv6=False):
    if is_ipv6:
        # ICMPv6 Echo Request tem tipo 128
        header = struct.pack('!BBHI', 128, 0, 0, identifier)
        payload = b'PythonTraceroute'
        checksum = calculate_checksum(header + payload)
        header = struct.pack('!BBHI', 128, 0, checksum, identifier)
    else:
        # ICMP Echo Request (IPv4) tem tipo 8
        header = struct.pack('!BBHHH', 8, 0, 0, identifier, sequence_number)
        payload = b'PythonTraceroute'
        checksum = calculate_checksum(header + payload)
        header = struct.pack('!BBHHH', 8, 0, checksum, identifier, sequence_number)
    return header + payload


def log_to_file(log_message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("traceroute.log", "a") as log_file:
        log_file.write(f"[{timestamp}] {log_message}\n")


def traceroute(destination, max_hops=30, initial_timeout=1):
    try:
        is_ipv6 = ":" in socket.gethostbyname(destination)
        proto_icmp = socket.IPPROTO_ICMP if not is_ipv6 else socket.IPPROTO_ICMPV6

        dest_addr = socket.getaddrinfo(destination, None, socket.AF_INET6 if is_ipv6 else socket.AF_INET)[0][4][0]
        print(f"Traceroute para {destination} ({dest_addr}), máximo de {max_hops} saltos:\n")
        log_to_file(f"Traceroute para {destination} ({dest_addr}), máximo de {max_hops} saltos:")

        times = []
        for ttl in range(1, max_hops + 1):
            send_socket = socket.socket(socket.AF_INET6 if is_ipv6 else socket.AF_INET, socket.SOCK_RAW, proto_icmp)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            send_socket.settimeout(initial_timeout)

            identifier = 12345
            sequence_number = ttl
            packet = create_icmp_packet(identifier, sequence_number, is_ipv6)

            start_time = time.time()
            send_socket.sendto(packet, (dest_addr, 0))

            try:
                data, addr = send_socket.recvfrom(512)
                end_time = time.time()
                elapsed_time = (end_time - start_time) * 1000  # RTT em ms
                ip_address = addr[0]

                try:
                    host_name = socket.gethostbyaddr(ip_address)[0]
                except socket.herror:
                    host_name = ip_address

                message = f"{ttl:2} {ip_address} ({host_name}) {elapsed_time:.2f} ms"
                print(message)
                log_to_file(message)
                times.append(elapsed_time)

                if ip_address == dest_addr:
                    print("\nDestino alcançado!")
                    log_to_file("Destino alcançado!")
                    break
            except socket.timeout:
                timeout_message = f"{ttl:2} * Request timed out."
                print(timeout_message)
                log_to_file(timeout_message)
                times.append(None)

                # Incrementa o timeout após 3 saltos consecutivos sem resposta
                if len(times) >= 3 and all(t is None for t in times[-3:]):
                    initial_timeout += 1
            finally:
                send_socket.close()

        else:
            print("\nNão foi possível alcançar o destino dentro do limite de saltos.")
            log_to_file("Não foi possível alcançar o destino dentro do limite de saltos.")

        plot_results(times)
    except socket.gaierror:
        print(f"Erro: Não foi possível resolver o host {destination}.")
        log_to_file(f"Erro: Não foi possível resolver o host {destination}.")
    except PermissionError:
        print("Erro: Permissões insuficientes. Execute como administrador ou com sudo.")
        log_to_file("Erro: Permissões insuficientes. Execute como administrador ou com sudo.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        log_to_file(f"Erro inesperado: {e}")


def plot_results(times):
    hops = list(range(1, len(times) + 1))
    valid_times = [t for t in times if t is not None]
    valid_hops = [h for h, t in zip(hops, times) if t is not None]

    plt.figure(figsize=(10, 6))
    plt.plot(valid_hops, valid_times, marker='o', color='b', label="RTT (ms)")
    plt.axhline(y=sum(valid_times) / len(valid_times), color='r', linestyle='--', label="Média RTT")
    plt.title("Traceroute - Tempo de Resposta por Salto")
    plt.xlabel("Saltos")
    plt.ylabel("Tempo de Resposta (ms)")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig("traceroute_graph.png")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: sudo python3 traceroute.py <destino>")
        sys.exit(1)

    target = sys.argv[1].strip()
    traceroute(target)

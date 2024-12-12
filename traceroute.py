import socket
import struct
import time
import sys
import matplotlib.pyplot as plt
from datetime import datetime


def calcular_checksum(dados):
    soma = sum((dados[i] << 8) + dados[i + 1] for i in range(0, len(dados) - len(dados) % 2, 2))
    soma += dados[-1] if len(dados) % 2 else 0
    soma = (soma >> 16) + (soma & 0xffff)
    return ~((soma + (soma >> 16)) & 0xffff) & 0xffff


def criar_pacote_icmp(identificador, sequencia, ipv6=False):
    tipo = 128 if ipv6 else 8  # ICMPv6 = 128; ICMPv4 = 8
    cabecalho = struct.pack('!BBHHH', tipo, 0, 0, identificador, sequencia)
    payload = b'PythonTraceroute'
    checksum = calcular_checksum(cabecalho + payload)
    return struct.pack('!BBHHH', tipo, 0, checksum, identificador, sequencia) + payload


def registrar_log(mensagem):
    with open("traceroute.log", "a") as log:
        log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {mensagem}\n")


def traceroute(destino, max_saltos=30, timeout=1):
    try:
        ipv6 = ":" in socket.gethostbyname(destino)
        protocolo_icmp = socket.IPPROTO_ICMPV6 if ipv6 else socket.IPPROTO_ICMP
        endereco = socket.getaddrinfo(destino, None, socket.AF_INET6 if ipv6 else socket.AF_INET)[0][4][0]

        print(f"Traceroute para {destino} ({endereco}), máximo de {max_saltos} saltos.\n")
        registrar_log(f"Traceroute para {destino} ({endereco}), máximo de {max_saltos} saltos.")
        tempos = []

        for ttl in range(1, max_saltos + 1):
            with socket.socket(socket.AF_INET6 if ipv6 else socket.AF_INET, socket.SOCK_RAW, protocolo_icmp) as soquete:
                soquete.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                soquete.settimeout(timeout)
                soquete.sendto(criar_pacote_icmp(12345, ttl, ipv6), (endereco, 0))
                inicio = time.time()

                try:
                    _, remetente = soquete.recvfrom(512)
                    rtt = (time.time() - inicio) * 1000
                    ip = remetente[0]
                    print(f"{ttl:2} {ip} {rtt:.2f} ms")
                    registrar_log(f"{ttl:2} {ip} {rtt:.2f} ms")
                    tempos.append(rtt)
                    if ip == endereco:
                        print("Destino alcançado!")
                        registrar_log("Destino alcançado!")
                        break
                except socket.timeout:
                    print(f"{ttl:2} * Tempo esgotado.")
                    registrar_log(f"{ttl:2} * Tempo esgotado.")
                    tempos.append(None)
                    if tempos[-3:] == [None] * 3:
                        timeout += 1

        gerar_grafico(tempos)
    except socket.gaierror:
        print(f"Erro: Não foi possível resolver o destino {destino}.")
        registrar_log(f"Erro: Não foi possível resolver o destino {destino}.")
    except PermissionError:
        print("Erro: Permissões insuficientes. Execute como administrador ou com sudo.")
        registrar_log("Erro: Permissões insuficientes.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        registrar_log(f"Erro inesperado: {e}")


def gerar_grafico(tempos):
    saltos = list(range(1, len(tempos) + 1))
    validos = [(h, t) for h, t in zip(saltos, tempos) if t is not None]
    if not validos:
        print("Nenhum dado válido para gerar o gráfico.")
        return

    hops, rtts = zip(*validos)
    plt.plot(hops, rtts, marker='o', label="RTT (ms)")
    plt.axhline(y=sum(rtts) / len(rtts), color='r', linestyle='--', label="Média RTT")
    plt.title("Traceroute - Tempo de Resposta por Salto")
    plt.xlabel("Salto")
    plt.ylabel("Tempo de Resposta (ms)")
    plt.grid()
    plt.legend()
    plt.savefig("traceroute_graph.png")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: sudo python3 traceroute.py <destino>")
        sys.exit(1)

    traceroute(sys.argv[1].strip())

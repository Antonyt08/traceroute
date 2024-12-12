import socket
import struct
import time

def checksum(data):
    """
    Função para calcular o checksum de um pacote.
    """
    sum = 0
    data = bytearray(data)

    # Soma de 2 bytes de cada vez
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            sum += (data[i] << 8) + data[i+1]
        else:
            sum += (data[i] << 8)

    # Complemento de 1 bit
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    return ~sum & 0xffff

def criar_pacote_icmp(id_processo):
    """
    Cria o pacote ICMP com tipo, código e checksum.
    """
    tipo = 8  # Tipo 8 é para requisição Echo (ping)
    codigo = 0
    checksum_valor = 0
    id_process = id_processo
    sequencia = 1

    # Criação do cabeçalho ICMP sem checksum
    pacote = struct.pack('bbHHh', tipo, codigo, checksum_valor, id_process, sequencia)

    # Calcula o checksum
    checksum_valor = checksum(pacote)

    # Recria o pacote ICMP com checksum correto
    pacote = struct.pack('bbHHh', tipo, codigo, checksum_valor, id_process, sequencia)

    return pacote

def traceroute(destino, max_hops=30, timeout=2):
    """
    Função para realizar o traceroute até o destino especificado.
    """
    endereco_destino = socket.gethostbyname(destino)
    print(f"Rastreando rota para {destino} ({endereco_destino}), máximo de {max_hops} saltos\n")

    porta_destino = 33434  # Porta padrão usada para traceroute
    ttl = 1  # Inicia com TTL = 1
    id_processo = 1  # Identificador do processo para o ICMP

    while ttl <= max_hops:
        # Cria o socket para enviar pacotes UDP
        socket_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        socket_envio.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        # Cria o socket para receber respostas ICMP
        socket_receber = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        socket_receber.settimeout(timeout)

        # Associa o socket receptor a uma porta local
        socket_receber.bind(("", porta_destino))

        # Cria o pacote ICMP
        pacote_icmp = criar_pacote_icmp(id_processo)

        # Envia o pacote ICMP
        socket_envio.sendto(pacote_icmp, (endereco_destino, porta_destino))
        inicio_tempo = time.time()

        try:
            # Aguarda por uma resposta do roteador
            dados, endereco_atual = socket_receber.recvfrom(512)
            tempo_decorrido = (time.time() - inicio_tempo) * 1000  # Calcula o tempo em ms
            endereco_atual = endereco_atual[0]

            # Tenta resolver o nome do host a partir do endereço IP
            try:
                nome_host = socket.gethostbyaddr(endereco_atual)[0]
            except socket.herror:
                nome_host = endereco_atual

            print(f"{ttl}\t{nome_host} ({endereco_atual})\t{tempo_decorrido:.2f} ms")
        except socket.timeout:
            # Se não receber resposta dentro do tempo limite
            print(f"{ttl}\t*\tTempo esgotado.")
            endereco_atual = None
        finally:
            # Fecha os sockets abertos
            socket_envio.close()
            socket_receber.close()

        ttl += 1  # Incrementa o TTL para o próximo salto

        # Verifica se chegou ao destino final
        if endereco_atual == endereco_destino:
            print("Destino alcançado.\n")
            break

if __name__ == "__main__":
    destino = input("Digite o destino (nome ou IP): ")
    traceroute(destino)

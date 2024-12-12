
# Traceroute em Python

Este projeto implementa uma ferramenta de **Traceroute** em Python utilizando **sockets** e o protocolo **ICMP** para rastrear o caminho de pacotes até um destino. O programa registra o tempo de resposta (RTT) de cada salto, gera um gráfico visual dos tempos de resposta e grava logs detalhados em um arquivo.

## Requisitos

- **Python 3** ou superior.
- Biblioteca **matplotlib** (para gerar gráficos).

Para instalar as dependências necessárias, você pode usar o `pip`:

```bash
sudo pip install matplotlib
```

## Funcionalidades

- Realiza um **traceroute** até um destino (endereço IP ou nome de domínio).
- Suporta **IPv4** e **IPv6**.
- Calcula o **tempo de resposta (RTT)** de cada salto intermediário.
- Grava as informações de cada salto no arquivo **traceroute.log**.
- Gera um gráfico visual mostrando o tempo de resposta por salto e o tempo médio.
- Aumenta automaticamente o **timeout** após 3 saltos consecutivos sem resposta.

## Como Usar

1. **Clone o repositório** ou baixe os arquivos do projeto.

2. **Execute o script** na linha de comando, fornecendo o destino (endereço IP ou nome de domínio):

   ```bash
   sudo python3 traceroute.py <destino>
   ```

   Exemplo:

   ```bash
   sudo python3 traceroute.py google.com
   ```

   - A execução pode requerer permissões de **root** (em sistemas baseados em Unix), devido ao uso de pacotes ICMP.

3. O programa exibirá os resultados do traceroute no terminal, mostrando os saltos, endereços IP dos roteadores e o tempo de resposta (RTT).

4. O arquivo de log **traceroute.log** será gerado com as informações de cada salto.

5. O gráfico **traceroute_graph.png** será salvo com o tempo de resposta (RTT) de cada salto.

### Como visualizar o gráfico gerado:

Após a execução do programa, o gráfico gerado será salvo como **traceroute_graph.png** na mesma pasta onde o script foi executado.

- **Para visualizar o gráfico no Windows**, use o seguinte comando:

  ```bash
  explorer.exe traceroute_graph.png
  ```

  Este comando abrirá o arquivo de imagem no visualizador de imagens padrão do Windows.

- **Para visualizar no Linux ou MacOS**, você pode abrir o arquivo diretamente com o visualizador de imagens de sua preferência (exemplo: `xdg-open traceroute_graph.png` no Linux).

## Exemplo de Saída

```text
Traceroute para google.com (142.250.72.174), máximo de 30 saltos:

 1  192.168.0.1 (router.local)  1.25 ms
 2  10.10.10.1 (isp-router)  9.82 ms
 3  142.250.72.174 (google.com)  15.22 ms

Destino alcançado!
```

## Como Funciona

1. O programa envia pacotes **ICMP Echo Request** (mensagens de "ping") para o destino.
2. A cada salto, o **TTL** (Time-To-Live) do pacote é incrementado.
3. O tempo de resposta de cada salto é calculado e exibido.
4. Quando o destino final for alcançado ou o número máximo de saltos for atingido, o programa se encerra.
5. O gráfico gerado mostra a variação do tempo de resposta (RTT) para cada salto no caminho até o destino, junto com a média dos tempos de resposta.

## Estrutura de Arquivos

- **traceroute.py**: Arquivo principal do programa, responsável pela execução do traceroute.
- **traceroute.log**: Arquivo de log gerado, contendo os detalhes dos saltos e tempos de resposta.
- **traceroute_graph.png**: Gráfico gerado com os tempos de resposta por salto.

## Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
```

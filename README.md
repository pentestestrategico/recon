# REDHUNT Recon Script

Script de reconhecimento para Bug Bounty que coleta subdominios, valida hosts ativos e gera uma triagem inicial com foco em alvos potencialmente interessantes.

## O que o script faz

1. Coleta subdominios de multiplas fontes:
- `subfinder`
- `crt.sh`
- `CertSpotter`

2. Remove duplicados e normaliza dominios.

3. Resolve os subdominios com `dnsx` para identificar hosts ativos.

4. Filtra hosts "juicy" por palavras-chave (ex.: `api`, `dev`, `admin`, `stage`, `qa`, `uat`, `internal`, `vpn`).

5. Executa `httpx` para obter status code e title dos hosts ativos.

6. Salva os resultados em arquivos.

## Estrutura de saida

Ao executar, o script cria uma pasta com o nome do dominio alvo (pontos substituidos por `_`).

Exemplo para `exemplo.com`:

- `exemplo_com/all_alive.txt`: todos os hosts ativos
- `exemplo_com/juicy_alive.txt`: hosts ativos que bateram no filtro juicy
- `exemplo_com/httpx_output.txt`: output do httpx (status code e title)

## Requisitos

- Python 3.8+
- Dependencia Python:
- `requests`

Ferramentas externas (precisam estar no `PATH`):
- `subfinder`
- `dnsx`
- `httpx`

## Instalacao

### 1) Instalar dependencia Python

```bash
pip install requests
```

### 2) Instalar ferramentas ProjectDiscovery

Voce pode instalar via Go:

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

Garanta que o diretorio de binarios do Go esteja no `PATH`.

## Como usar

Na raiz do projeto:

```bash
python recon.py
```

Depois informe o dominio quando solicitado:

```text
Digite o dominio alvo (ex: exemplo.com):
```

## Exemplo de fluxo

```text
[+] Coletando subdominios...
[+] subfinder: X encontrados
[+] crtsh: Y encontrados
[+] certspotter: Z encontrados
[+] Hosts ativos: N
[+] Juicy encontrados: M
[+] HTTPX resultados: K
```

## Observacoes

- O script depende de acesso a internet para consultas em APIs/public sources.
- Se uma fonte falhar, o script continua com as demais.
- O filtro juicy e simples e baseado em regex; ajuste conforme seu contexto.

## Uso responsavel

Execute apenas em ativos autorizados e dentro do escopo permitido do programa de Bug Bounty.

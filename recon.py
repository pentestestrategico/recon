#!/usr/bin/env python3

import subprocess
import requests
import re
import os

# -----------------------------
# Banner
# -----------------------------
def banner():
    print("""
========================================
           🔴 REDHUNT 🔴
   Recon Framework - Bug Bounty Edition
----------------------------------------
   www.redhuntsecurity.com.br
========================================
""")

# -----------------------------
# Utils
# -----------------------------
def run_cmd_list(cmd_list):
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"[ERRO] {' '.join(cmd_list)}")
            print(result.stderr)

        return result.stdout.splitlines()

    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return []

def clean_domain(d):
    return d.strip().lower().replace("*.", "")

# -----------------------------
# Sources
# -----------------------------
def subfinder(domain):
    print("[+] Rodando subfinder...")
    return run_cmd_list(["subfinder", "-d", domain, "-silent"])

def crtsh(domain):
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        data = requests.get(url, timeout=10).json()
        return [
            clean_domain(x)
            for entry in data
            for x in entry["name_value"].split("\n")
        ]
    except:
        return []

def certspotter(domain):
    try:
        url = f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"
        data = requests.get(url, timeout=10).json()
        return [
            clean_domain(d)
            for entry in data
            for d in entry.get("dns_names", [])
        ]
    except:
        return []

# -----------------------------
# DNS
# -----------------------------
def resolve_bulk(domains):
    print("[+] Resolvendo com dnsx...")

    try:
        process = subprocess.Popen(
            ["dnsx", "-silent"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        input_data = "\n".join(domains)
        output, _ = process.communicate(input_data)

        return set(output.splitlines())

    except Exception as e:
        print(f"[dnsx erro]: {e}")
        return set()

# -----------------------------
# HTTPX
# -----------------------------
def run_httpx(domains, output_file):
    print("[+] Rodando httpx...")

    try:
        process = subprocess.Popen(
            ["httpx", "-silent", "-title", "-status-code"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        input_data = "\n".join(domains)
        output, _ = process.communicate(input_data)

        lines = output.splitlines()

        with open(output_file, "w") as f:
            f.write("\n".join(lines))

        return lines

    except Exception as e:
        print(f"[httpx erro]: {e}")
        return []

# -----------------------------
# Main
# -----------------------------
def main():
    banner()

    domain = input("Digite o domínio alvo (ex: exemplo.com): ").strip()

    if not domain:
        print("[-] Domínio inválido")
        return

    # -----------------------------
    # Criar pasta
    # -----------------------------
    folder = domain.replace(".", "_")
    os.makedirs(folder, exist_ok=True)

    OUTPUT_ALL = os.path.join(folder, "all_alive.txt")
    OUTPUT_JUICY = os.path.join(folder, "juicy_alive.txt")
    OUTPUT_HTTPX = os.path.join(folder, "httpx_output.txt")

    print(f"\n[+] Recon iniciado para: {domain}")
    print(f"[+] Pasta criada: {folder}\n")

    all_subs = set()

    # -----------------------------
    # Coleta
    # -----------------------------
    print("[+] Coletando subdomínios...")

    subs1 = subfinder(domain)
    print(f"[+] subfinder: {len(subs1)} encontrados")

    subs2 = crtsh(domain)
    print(f"[+] crtsh: {len(subs2)} encontrados")

    subs3 = certspotter(domain)
    print(f"[+] certspotter: {len(subs3)} encontrados")

    for s in subs1 + subs2 + subs3:
        if domain in s:
            all_subs.add(clean_domain(s))

    print(f"[+] Total único coletado: {len(all_subs)}")

    if not all_subs:
        print("[!] Nenhum subdomínio encontrado")
        return

    # -----------------------------
    # DNS
    # -----------------------------
    alive = resolve_bulk(all_subs)
    print(f"[+] Hosts ativos: {len(alive)}")

    if not alive:
        print("[!] Nenhum host ativo")
        return

    # -----------------------------
    # Juicy
    # -----------------------------
    juicy_regex = re.compile(
        r"(api|dev|test|admin|stage|stg|qa|uat|internal|vpn)",
        re.I
    )

    juicy = {d for d in alive if juicy_regex.search(d)}
    print(f"[+] Juicy encontrados: {len(juicy)}")

    # -----------------------------
    # HTTPX
    # -----------------------------
    httpx_results = run_httpx(alive, OUTPUT_HTTPX)
    print(f"[+] HTTPX resultados: {len(httpx_results)}")

    # -----------------------------
    # Save
    # -----------------------------
    with open(OUTPUT_ALL, "w") as f:
        f.write("\n".join(sorted(alive)))

    with open(OUTPUT_JUICY, "w") as f:
        f.write("\n".join(sorted(juicy)))

    # -----------------------------
    # RESUMO FINAL
    # -----------------------------
    print("\n[+] RESUMO FINAL 📊")
    print(f"[+] {OUTPUT_ALL}: {len(alive)} domínios")
    print(f"[+] {OUTPUT_JUICY}: {len(juicy)} domínios")
    print(f"[+] {OUTPUT_HTTPX}: {len(httpx_results)} resultados")

    print("\n[+] RECON FINALIZADO 🚀")

# -----------------------------
if __name__ == "__main__":
    main()
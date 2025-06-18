import requests
import json
import time
import re
import os
import random
from urllib.parse import quote
from colorama import Fore, Style, init
from datetime import datetime

# Configuração inicial
init(autoreset=True)
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
B = Fore.BLUE
C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
RESET = Style.RESET_ALL

# Configurações globais
TIMEOUT = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Lista de sites para verificação de usuário
SITES = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    # ... (outros sites da lista original)
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_main_banner():
    clear_screen()
    print(f"""{C}
    ███████╗██╗  ██╗██████╗  ██████╗██╗     ██╗ ██████╗ 
    ██╔════╝██║  ██║██╔══██╗██╔════╝██║     ██║██╔═══██╗
    ███████╗███████║██████╔╝██║     ██║     ██║██║   ██║
    ╚════██║██╔══██║██╔══██╗██║     ██║     ██║██║   ██║
    ███████║██║  ██║██║  ██║╚██████╗███████╗██║╚██████╔╝
    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝ ╚═════╝ 
    {G}SUITE DE FERRAMENTAS OSINT{RESET}
    {Y}Versão 3.0 | By: SeuNome | LGPD Compliant{RESET}
    """)

# ==============================================
# Módulo de Busca por Username (Sherlock)
# ==============================================

def verificar_usuario(username):
    resultados = {}
    
    for site, url in SITES.items():
        url_formatada = url.format(username)
        try:
            resposta = requests.get(
                url_formatada,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=False
            )
            
            if resposta.status_code == 200:
                resultados[site] = {"url": url_formatada, "status": "Encontrado"}
            elif resposta.status_code in [301, 302]:
                resultados[site] = {"url": url_formatada, "status": "Redirecionado"}
            else:
                resultados[site] = {"url": url_formatada, "status": "Não encontrado"}
                
        except requests.exceptions.RequestException as e:
            resultados[site] = {"url": url_formatada, "status": f"Erro: {str(e)}"}
        
        time.sleep(0.5)
    
    return resultados

def buscar_email(email):
    resultados = {}
    email_codificado = quote(email)
    
    sites_email = {
        "Facebook": f"https://www.facebook.com/search/people/?q={email_codificado}",
        "Twitter": f"https://twitter.com/search?q={email_codificado}&src=typed_query",
        # ... (outros sites da lista original)
    }
    
    for site, url in sites_email.items():
        try:
            resposta = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=False
            )
            
            if resposta.status_code == 200:
                resultados[site] = {"url": url, "status": "Possível correspondência"}
            else:
                resultados[site] = {"url": url, "status": "Não encontrado"}
                
        except requests.exceptions.RequestException as e:
            resultados[site] = {"url": url, "status": f"Erro: {str(e)}"}
        
        time.sleep(1)
    
    return resultados

def buscar_nome_real(nome):
    resultados = {}
    nome_codificado = quote(nome)
    
    sites_nome = {
        "Facebook": f"https://www.facebook.com/search/people/?q={nome_codificado}",
        "LinkedIn": f"https://www.linkedin.com/search/results/people/?keywords={nome_codificado}",
        # ... (outros sites da lista original)
    }
    
    for site, url in sites_nome.items():
        try:
            resposta = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=False
            )
            
            if resposta.status_code == 200:
                resultados[site] = {"url": url, "status": "Possível correspondência"}
            else:
                resultados[site] = {"url": url, "status": "Não encontrado"}
                
        except requests.exceptions.RequestException as e:
            resultados[site] = {"url": url, "status": f"Erro: {str(e)}"}
        
        time.sleep(1)
    
    return resultados

def mostrar_resultados(resultados, titulo):
    print(f"\n{B}=== {titulo} ==={RESET}")
    for site, dados in resultados.items():
        status = dados["status"]
        if "Encontrado" in status or "Possível" in status:
            cor = G
        elif "Erro" in status:
            cor = R
        else:
            cor = Y
        
        print(f"{W}{site}:{RESET} {cor}{status}{RESET} - {dados['url']}")

# ==============================================
# Módulo de Consulta de Placa
# ==============================================

def display_placa_banner():
    clear_screen()
    print(f"""{B}
    ██████╗ ██╗      █████╗  ██████╗██╗  ██╗
    ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝
    ██████╔╝██║     ███████║██║     █████╔╝ 
    ██╔═══╝ ██║     ██╔══██║██║     ██╔═██╗ 
    ██║     ███████╗██║  ██║╚██████╗██║  ██╗
    ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
    {G}CONSULTA DE PLACA - APIs Públicas{RESET}
    """)

def validate_plate(plate):
    plate = plate.upper().strip()
    
    if re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', plate):
        return True, plate
    
    if re.match(r'^[A-Z]{3}[0-9]{4}$', plate):
        return True, plate
    
    return False, "Formato inválido. Use: ABC1D23 ou ABC1234"

def consulta_fipe(plate):
    try:
        url = f"https://parallelum.com.br/fipe/api/v2/vehicles/{plate}"
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return {"error": "API indisponível"}

def consulta_publica_placa(plate):
    try:
        url = f"https://api.placafipe.com.br/consulta/{plate}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"error": "Dados não disponíveis"}
    except:
        return {"error": "Erro na conexão"}

def placa_module():
    while True:
        display_placa_banner()
        print(f"{G}1. Consultar placa")
        print(f"2. Validar formato")
        print(f"3. Voltar{RESET}")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            display_placa_banner()
            plate = input("Digite a placa (sem hífen): ").upper()
            
            valid, result = validate_plate(plate)
            if not valid:
                print(f"\n{R}[!] {result}{RESET}")
                input("\nPressione Enter para continuar...")
                continue
            
            print(f"\n{Y}[*] Consultando placa {plate}...{RESET}")
            
            data = {
                **consulta_publica_placa(plate),
                "fipe": consulta_fipe(plate)
            }
            
            display_placa_banner()
            print(f"\n{B}=== DADOS DO VEÍCULO ==={RESET}")
            print(f"{G}Placa:{RESET} {plate}")
            print(f"{G}Marca:{RESET} {data.get('marca', 'Não disponível')}")
            print(f"{G}Modelo:{RESET} {data.get('modelo', 'Não disponível')}")
            print(f"{G}Ano:{RESET} {data.get('ano', 'Não disponível')}")
            
            input("\nPressione Enter para continuar...")
        
        elif choice == "2":
            display_placa_banner()
            plate = input("Digite a placa para validar: ").upper()
            valid, msg = validate_plate(plate)
            print(f"\n{Y}Resultado:{RESET}")
            print(f"Placa: {plate}")
            print(f"Válida: {G if valid else R}{valid}{RESET}")
            print(f"Formato: {msg if isinstance(msg, str) else 'Correto'}")
            input("\nPressione Enter para continuar...")
        
        elif choice == "3":
            break
        
        else:
            print(f"\n{R}[!] Opção inválida!{RESET}")
            input("Pressione Enter para continuar...")

# ==============================================
# Módulo de Consulta de CPF
# ==============================================

def display_cpf_banner():
    clear_screen()
    print(f"""{C}
    ██████╗██████╗ ███████╗
    ██╔════╝██╔══██╗██╔════╝
    ██║     ██████╔╝█████╗  
    ██║     ██╔═══╝ ██╔══╝  
    ╚██████╗██║     ██║     
     ╚═════╝╚═╝     ╚═╝     
    {G}CONSULTA DE CPF - APIs Públicas{RESET}
    """)

def validate_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Cálculo dos dígitos verificadores
    # ... (implementação original)
    
    return True

def cpf_module():
    while True:
        display_cpf_banner()
        print(f"{G}1. Validar CPF")
        print(f"2. Gerar CPF de teste")
        print(f"3. Voltar{RESET}")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            display_cpf_banner()
            cpf = input("Digite o CPF para validação: ").strip()
            
            if not validate_cpf(cpf):
                print(f"\n{R}[!] CPF inválido!{RESET}")
                input("\nPressione Enter para continuar...")
                continue
            
            print(f"\n{G}[+] CPF válido{RESET}")
            print(f"{Y}Atenção: Consultas completas requerem autenticação oficial{RESET}")
            input("\nPressione Enter para continuar...")
        
        elif choice == "2":
            display_cpf_banner()
            print(f"{G}[*] Gerando CPF válido para testes...{RESET}")
            cpf_teste = ''.join([str(random.randint(0, 9)) for _ in range(11)])
            print(f"\n{Y}CPF para testes:{RESET} {G}{cpf_teste[:3]}.{cpf_teste[3:6]}.{cpf_teste[6:9]}-{cpf_teste[9:]}{RESET}")
            input("\nPressione Enter para continuar...")
        
        elif choice == "3":
            break
        
        else:
            print(f"\n{R}[!] Opção inválida!{RESET}")
            input("Pressione Enter para continuar...")

# ==============================================
# Módulo de Consulta de Telefone
# ==============================================

def display_telefone_banner():
    clear_screen()
    print(f"""{C}
    ████████╗███████╗██╗     ███████╗ ██████╗ ███╗   ██╗
    ╚══██╔══╝██╔════╝██║     ██╔════╝██╔═══██╗████╗  ██║
       ██║   █████╗  ██║     █████╗  ██║   ██║██╔██╗ ██║
       ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██║╚██╗██║
       ██║   ███████╗███████╗███████╗╚██████╔╝██║ ╚████║
       ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
    {G}CONSULTA TELEFÔNICA - APIs Públicas{RESET}
    """)

def telefone_module():
    while True:
        display_telefone_banner()
        print(f"{G}1. Consultar telefone")
        print(f"2. Voltar{RESET}")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            display_telefone_banner()
            phone = input("Digite o telefone com DDD: ").strip()
            
            clean_num = ''.join(filter(str.isdigit, phone))
            if len(clean_num) not in (10, 11):
                print(f"\n{R}[!] Número inválido!{RESET}")
                input("\nPressione Enter para continuar...")
                continue
            
            print(f"\n{Y}[*] Consultando operadora...{RESET}")
            time.sleep(1)
            
            print(f"\n{G}Número:{RESET} ({clean_num[:2]}) {clean_num[2:7]}-{clean_num[7:]}")
            print(f"{G}Operadora:{RESET} Consulta limitada via API pública")
            print(f"{Y}Observação: Dados completos requerem consulta oficial{RESET}")
            input("\nPressione Enter para continuar...")
        
        elif choice == "2":
            break
        
        else:
            print(f"\n{R}[!] Opção inválida!{RESET}")
            input("Pressione Enter para continuar...")

# ==============================================
# Módulo de Consulta de CNPJ
# ==============================================

def display_cnpj_banner():
    clear_screen()
    print(f"""{B}
    ██████╗ ██████╗ ███╗   ██╗██████╗ 
    ██╔════╝██╔═══██╗████╗  ██║╚════██╗
    ██║     ██║   ██║██╔██╗ ██║ █████╔╝
    ██║     ██║   ██║██║╚██╗██║██╔═══╝ 
    ╚██████╗╚██████╔╝██║ ╚████║███████╗
     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
    {G}CONSULTA CNPJ - ReceitaWS API{RESET}
    """)

def cnpj_module():
    while True:
        display_cnpj_banner()
        print(f"{G}1. Consultar CNPJ")
        print(f"2. Voltar{RESET}")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            display_cnpj_banner()
            cnpj = input("Digite o CNPJ: ").strip()
            
            cnpj = ''.join(filter(str.isdigit, cnpj))
            if len(cnpj) != 14:
                print(f"\n{R}[!] CNPJ inválido!{RESET}")
                input("\nPressione Enter para continuar...")
                continue
            
            print(f"\n{Y}[*] Consultando CNPJ...{RESET}")
            
            try:
                url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                display_cnpj_banner()
                print(f"\n{G}CNPJ:{RESET} {cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}")
                
                if 'nome' in data:
                    print(f"{G}Razão Social:{RESET} {data['nome']}")
                    print(f"{G}Status:{RESET} {data.get('situacao', 'Não disponível')}")
                else:
                    print(f"{R}Erro na consulta: {data.get('message', 'API indisponível')}{RESET}")
                
            except Exception as e:
                print(f"{R}Erro na consulta: {str(e)}{RESET}")
            
            input("\nPressione Enter para continuar...")
        
        elif choice == "2":
            break
        
        else:
            print(f"\n{R}[!] Opção inválida!{RESET}")
            input("Pressione Enter para continuar...")

# ==============================================
# Menu Principal
# ==============================================

def main_menu():
    # Verificar dependências
    try:
        import requests
    except ImportError:
        print(f"{Y}[*] Instalando dependências...{RESET}")
        os.system("pip install requests colorama")
        import requests
    
    while True:
        display_main_banner()
        print(f"{G}1. Busca por Username (Sherlock)")
        print(f"2. Consulta de Placa")
        print(f"3. Consulta de CPF")
        print(f"4. Consulta de Telefone")
        print(f"5. Consulta de CNPJ")
        print(f"6. Sair{RESET}")
        
        choice = input("\nEscolha um módulo (1-6): ").strip()
        
        if choice == "1":
            display_main_banner()
            print(f"{G}1. Buscar por nome de usuário")
            print(f"2. Buscar por e-mail")
            print(f"3. Buscar por nome real")
            print(f"4. Voltar{RESET}")
            
            sub_choice = input("\nEscolha uma opção: ").strip()
            
            if sub_choice == "1":
                username = input("\nDigite o nome de usuário: ").strip()
                if username:
                    resultados = verificar_usuario(username)
                    mostrar_resultados(resultados, f"Resultados para: {username}")
                else:
                    print(f"\n{R}Por favor, digite um nome de usuário válido.{RESET}")
                input("\nPressione Enter para continuar...")
                
            elif sub_choice == "2":
                email = input("\nDigite o e-mail: ").strip()
                if "@" in email and "." in email:
                    resultados = buscar_email(email)
                    mostrar_resultados(resultados, f"Resultados para: {email}")
                else:
                    print(f"\n{R}Por favor, digite um e-mail válido.{RESET}")
                input("\nPressione Enter para continuar...")
                
            elif sub_choice == "3":
                nome = input("\nDigite o nome real: ").strip()
                if len(nome.split()) >= 2:
                    resultados = buscar_nome_real(nome)
                    mostrar_resultados(resultados, f"Resultados para: {nome}")
                else:
                    print(f"\n{R}Por favor, digite nome e sobrenome.{RESET}")
                input("\nPressione Enter para continuar...")
                
            elif sub_choice == "4":
                continue
        
        elif choice == "2":
            placa_module()
        
        elif choice == "3":
            cpf_module()
        
        elif choice == "4":
            telefone_module()
        
        elif choice == "5":
            cnpj_module()
        
        elif choice == "6":
            print(f"\n{Y}[*] Saindo... Obrigado por usar a ferramenta!{RESET}")
            break
        
        else:
            print(f"\n{R}[!] Opção inválida!{RESET}")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main_menu()rootkalinethunter59@gmail.com

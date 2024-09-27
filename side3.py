import requests
import tkinter as tk
from tkinter import StringVar
from seleniumwire import webdriver  # Para interceptar requisições
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
from req1_pb2 import RequestData, ResponseData  # Certifique-se que o Protobuf gerou as classes corretamente

# Lista para armazenar os drivers de múltiplas janelas
drivers = []

# Função para iniciar o Selenium e carregar a página em uma nova janela
def iniciar_selenium_perfil(perfil_numero):
    try:
        PATH = "C:/Program Files (x86)/chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        service = Service(PATH)
        driver = webdriver.Chrome(service=service, options=options)
        drivers.append(driver)  # Adiciona o driver à lista de drivers

        # Acessa a página de login
        driver.get("https://9f.com/br/m/login")

        # Inserir número de celular e senha
        if perfil_numero == 1:
            driver.find_element(By.XPATH, "//input[@placeholder='Número de Celular']").send_keys("73988151400")
        else:
            driver.find_element(By.XPATH, "//input[@placeholder='Número de Celular']").send_keys(f"7398814{perfil_numero:03d}")
        
        driver.find_element(By.XPATH, "//input[@placeholder='Senha']").send_keys("indio123")
        driver.find_element(By.XPATH, "//button[text()='Login']").click()

        # Esperar a página carregar
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        driver.execute_script("document.body.style.zoom = '70%'")

        print(f"Página carregada com sucesso no Perfil {perfil_numero}.")
    
    except Exception as e:
        print(f"Erro ao executar o Selenium no perfil {perfil_numero}: {e}")

# Função para iniciar múltiplas janelas (perfis)
def iniciar_multiplos_perfis(numero_de_perfis):
    for i in range(1, numero_de_perfis + 1):
        thread = threading.Thread(target=iniciar_selenium_perfil, args=(i,))
        thread.daemon = True
        thread.start()

# Função para adicionar o listener ao campo 'EditBoxId_1' em todos os perfis
def adicionar_listener():
    for idx, driver in enumerate(drivers, 1):
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'EditBoxId_1')))
            # Adicionar listener
            driver.execute_script(f"""
                var inputBox = document.getElementById('EditBoxId_1');
                if (inputBox) {{
                    inputBox.addEventListener('input', function() {{
                        console.log("Perfil {idx}: " + this.value);
                    }});
                    console.log("Listener ativado no Perfil {idx}.");
                }}
            """)
        except Exception as e:
            print(f"Erro ao ativar o listener no perfil {idx}: {e}")

# Função para capturar o token da primeira requisição
def capturar_token(driver):
    try:
        # Verifica se a URL correta contém o token
        for request in driver.requests:
            if 'tadagaming.com/fg/req?D=2' in request.url:
                token = request.headers.get('token')
                if token:
                    print(f"Token capturado: {token}")
                    return token
    except Exception as e:
        print(f"Erro ao capturar o token: {e}")
    return None

# Função para enviar o valor capturado para o campo 'EditBoxId_1' nos navegadores
def enviar_valor_navegador(*args):
    valor = valor_capturado.get()  # Captura o valor do input na interface Tkinter

    for idx, driver in enumerate(drivers, 1):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'EditBoxId_1')))
            # Atualiza o valor do campo e dispara o evento de input
            driver.execute_script(f"""
                var input = document.getElementById('EditBoxId_1');
                if (input) {{
                    input.value = '{valor}';
                    var event = new Event('input', {{ bubbles: true }});
                    input.dispatchEvent(event);
                    console.log("Valor '{valor}' inserido no campo de entrada do Perfil {idx}.");
                }}
            """)
        except Exception as e:
            print(f"Erro ao enviar valor para o perfil {idx}: {e}")

# Função para enviar a requisição via requests e processar a resposta
def enviar_requisicao_via_requests(token, valor_input):
    headers = {
        "accept": "*/*",
        "content-type": "application/x-protobuf",  # Tipo de conteúdo esperado
        "origin": "https://wbgame.tadagaming.com",
        "referer": "https://wbgame.tadagaming.com/",
        "token": token,
        "user-agent": "Mozilla/5.0"
    }

    # Criar a mensagem Protobuf e definir o valor
    request_data = RequestData()
    request_data.valor_input = valor_input  # Ajuste conforme seu `.proto`

    # Serializar a mensagem Protobuf
    valor_input_bytes = request_data.SerializeToString()

    try:
        response = requests.post(
            'https://wbslot-fd-na.tadagaming.com/fg/req?D=39&',
            headers=headers,
            data=valor_input_bytes
        )
        if response.status_code == 200:
            print(f"Requisição enviada com sucesso. Resposta: {response.content}")
            processar_resposta_protobuf(response.content)
        else:
            print(f"Erro na requisição. Status Code: {response.status_code}, Resposta: {response.content}")
    except Exception as e:
        print(f"Erro ao enviar a requisição: {e}")

# Função para processar e deserializar a resposta Protobuf
def processar_resposta_protobuf(response_bytes):
    response_data = ResponseData()
    response_data.ParseFromString(response_bytes)

    # Exibir todos os campos disponíveis na resposta
    print(f"Resposta completa: {response_data}")
    
    # Exemplo de acesso a campos individuais
    if hasattr(response_data, 'status_code'):
        print(f"Código de Status: {response_data.status_code}")
    if hasattr(response_data, 'mensagem'):
        print(f"Mensagem: {response_data.mensagem}")

# Função principal que captura o token e realiza a requisição
def acao_completa(driver, valor_input):
    token = capturar_token(driver)
    if token:
        enviar_requisicao_via_requests(token, valor_input)

# Interface com Tkinter
root = tk.Tk()
root.title("Automação de Requisição XHR e EditBox")

valor_capturado = StringVar()
valor_capturado.trace_add("write", enviar_valor_navegador)

label_valor = tk.Label(root, text="Digite algo:")
label_valor.grid(row=0, column=0, padx=10, pady=10)

entry_valor = tk.Entry(root, textvariable=valor_capturado, width=40)
entry_valor.grid(row=0, column=1, padx=10, pady=10)

botao_listener = tk.Button(root, text="Ativar Listener", command=adicionar_listener)
botao_listener.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

botao_executar = tk.Button(root, text="Executar Ação", command=lambda: acao_completa(drivers[0], valor_capturado.get()))
botao_executar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

iniciar_multiplos_perfis(1)

root.mainloop()

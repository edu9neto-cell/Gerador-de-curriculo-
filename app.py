# Gerador de Currículo: projeto escolar
# Usa somente a biblioteca padrão do Python: nada para instalar.
import os
from http.server import ThreadingHTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from html import escape
 
PASTA = os.path.dirname(os.path.abspath(__file__))
PORTA = 8000
 
# Código de cada habilidade (value do checkbox) e o texto exibido
HABILIDADES = {
    "html": "HTML",
    "css": "CSS",
    "python": "Python",
    "sql": "Banco de dados (SQL)",
    "git": "Git e GitHub",
    "office": "Pacote Office",
    "equipe": "Trabalho em equipe",
    "comunicacao": "Comunicação",
}
 
NIVEIS_INGLES = {
    "nenhum": "",
    "basico": "Inglês básico",
    "intermediario": "Inglês intermediário",
    "avancado": "Inglês avançado",
}
 
TEMAS = ["petroleo", "vinho", "grafite"]
 
# Dados fictícios para testar o sistema sem digitar tudo
EXEMPLO = {
    "nome": "ana beatriz da silva",
    "cargo": "Estágio em Desenvolvimento de Sistemas",
    "email": "ana.silva@email.com",
    "telefone": "81912345678",
    "cidade": "Barreiros, PE",
    "resumo": "Estudante do curso técnico de Desenvolvimento de "
              "Sistemas. Gosto de resolver problemas com "
              "programação e de aprender em equipe.",
    "curso": "Técnico em Desenvolvimento de Sistemas",
    "instituicao": "Escola Técnica Estadual",
    "ano": "2027",
    "situacao": "cursando",
    "exp_titulo": "Cardápio Digital (projeto escolar)",
    "exp_local": "Escola Técnica Estadual",
    "exp_periodo": "2026",
    "exp_descricao": "Site de lanchonete com HTML e CSS.\n"
                     "Cálculo dos pedidos em Python.",
    "habilidades": ["html", "css", "python", "equipe"],
    "outras": "Canva, lógica de programação",
    "ingles": "basico",
    "tema": "petroleo",
}
 
 
# ---------- 1. Funções de apoio ----------
 
def ler_arquivo(nome):
    """Lê um arquivo de texto da pasta do projeto."""
    caminho = os.path.join(PASTA, nome)
    with open(caminho, encoding="utf-8") as arquivo:
        return arquivo.read()
 
 
def campo(dados, nome):
    """Pega o valor de um campo enviado pelo formulário."""
    return dados.get(nome, [""])[0].strip()
def formatar_nome(texto):
    """Transforma 'ana da silva' em 'Ana da Silva'."""
    pequenas = ["da", "de", "do", "das", "dos", "e"]
    partes = []
    for palavra in texto.lower().split():
        if palavra in pequenas:
            partes.append(palavra)
        else:
            partes.append(palavra.capitalize())
    return " ".join(partes)
 
 
def so_numeros(texto):
    """Guarda só os dígitos: '(81) 9 1234' vira '8191234'."""
    numeros = ""
    for letra in texto:
        if letra.isdigit():
            numeros = numeros + letra
    return numeros
 
 
def formatar_telefone(texto):
    """Transforma '81912345678' em '(81) 91234-5678'."""
    n = so_numeros(texto)
    if len(n) == 11:
        return f"({n[:2]}) {n[2:7]}-{n[7:]}"
    if len(n) == 10:
        return f"({n[:2]}) {n[2:6]}-{n[6:]}"
    return ""
 
 
def email_valido(email):
    """Confere o formato básico: nome@site.algo, sem espaços."""
    if " " in email or email.count("@") != 1:
        return False
    usuario, site = email.split("@")
    return usuario != "" and "." in site and not site.endswith(".")
 
 
def com_quebras(texto):
    """Protege o texto e troca cada Enter por <br>."""
    return escape(texto).replace("\n", "<br>")
 
 
# ---------- 2. Leitura e validação ----------
 
def ler_formulario(dados):
    """Organiza os dados enviados pelo navegador."""
    form = {}
    for nome in ["nome", "cargo", "email", "telefone", "cidade",
                 "resumo", "curso", "instituicao", "ano",
                 "situacao", "exp_titulo", "exp_local",
                 "exp_periodo", "exp_descricao", "outras",
                 "ingles", "tema"]:
        form[nome] = campo(dados, nome)
    form["resumo"] = form["resumo"].replace("\r\n", "\n")
    form["exp_descricao"] = form["exp_descricao"].replace("\r\n", "\n")
    form["habilidades"] = dados.get("hab", [])
    if form["ingles"] not in NIVEIS_INGLES:
        form["ingles"] = "nenhum"
    if form["tema"] not in TEMAS:
        form["tema"] = "petroleo"
    return form
 
 
def validar(form):
    """Confere os campos. Devolve a lista de erros."""
    erros = []
    if form["nome"] == "":
        erros.append("Informe seu nome completo.")
    elif len(form["nome"].split()) < 2:
        erros.append("Escreva nome e sobrenome.")
    if form["cargo"] == "":
        erros.append("Informe o cargo ou objetivo.")
    if not email_valido(form["email"]):
        erros.append("Digite um e-mail válido, como nome@email.com.")
    telefone = formatar_telefone(form["telefone"])
    if form["telefone"] != "" and telefone == "":
        erros.append("O telefone precisa ter DDD e 8 ou 9 dígitos.")
    if form["curso"] == "" or form["instituicao"] == "":
        erros.append("Preencha o curso e a instituição.")
    ano = form["ano"]
    if ano != "":
        if not ano.isdigit() or not 1980 <= int(ano) <= 2040:
            erros.append("Ano inválido: use 4 dígitos, de 1980 a 2040.")
    if form["situacao"] not in ["cursando", "concluido"]:
        erros.append("Marque se o curso está cursando ou concluído.")
    if not form["habilidades"] and form["outras"] == "":
        erros.append("Marque ou escreva pelo menos uma habilidade.")
    return erros
 
 
# ---------- 3. Montagem do currículo ----------
 
def lista_habilidades(form):
    """Junta as marcadas e as digitadas, sem repetir."""
    lista = []
    for codigo in form["habilidades"]:
        if codigo in HABILIDADES:
            lista.append(HABILIDADES[codigo])
    for item in form["outras"].split(","):
        item = item.strip()
        if item != "" and item not in lista:
            lista.append(item)
    return lista
 
 
def montar_mensagens(lista):
    """Transforma a lista de (tipo, texto) em parágrafos."""
    html = ""
    for tipo, texto in lista:
        html += f'<p class="mensagem {tipo}">{escape(texto)}</p>\n'
    return html
 
 
def montar_curriculo(form):
    """Cria o HTML do currículo com os dados do formulário."""
    nome = escape(formatar_nome(form["nome"]))
    contato = [escape(form["email"])]
    if form["telefone"] != "":
        contato.append(formatar_telefone(form["telefone"]))
    if form["cidade"] != "":
        contato.append(escape(form["cidade"]))
 
    situacao = "Cursando"
    if form["situacao"] == "concluido":
        situacao = "Concluído"
    if form["ano"] != "":
        situacao += f" (conclusão em {form['ano']})"
 
    linha_contato = " | ".join(contato)
    html = f"""<article class="curriculo tema-{form['tema']}">
<div class="cv-topo">
<h3>{nome}</h3>
<p class="cv-cargo">{escape(form['cargo'])}</p>
<p class="cv-contato">{linha_contato}</p>
</div>\n"""
 
    if form["resumo"] != "":
        resumo = com_quebras(form["resumo"])
        html += f"<h4>Resumo</h4>\n<p>{resumo}</p>\n"
 
    html += f"""<h4>Formação</h4>
<p><strong>{escape(form['curso'])}</strong></p>
<p>{escape(form['instituicao'])}. {situacao}.</p>\n"""
 
    if form["exp_titulo"] != "":
        detalhes = []
        for chave in ["exp_local", "exp_periodo"]:
            if form[chave] != "":
                detalhes.append(escape(form[chave]))
        html += "<h4>Experiência e projetos</h4>\n"
        titulo = escape(form["exp_titulo"])
        html += f"<p><strong>{titulo}</strong></p>\n"
        if detalhes:
            html += f"<p>{' | '.join(detalhes)}</p>\n"
        if form["exp_descricao"] != "":
            html += f"<p>{com_quebras(form['exp_descricao'])}</p>\n"
 
    itens = ""
    for habilidade in lista_habilidades(form):
        itens += f"<li>{escape(habilidade)}</li>"
    html += "<h4>Habilidades</h4>\n"
    html += f'<ul class="cv-habilidades">{itens}</ul>\n'
 
    idioma = NIVEIS_INGLES[form["ingles"]]
    if idioma != "":
        html += f"<h4>Idiomas</h4>\n<p>{idioma}</p>\n"
 
    html += "</article>"
    return html
 
 
def montar_pagina(form, acao):
    """Decide o que mostrar e preenche as marcações do index.html."""
    mensagens = []
    curriculo = ('<p class="vazio">Preencha o formulário e clique em '
                 'Gerar currículo.</p>')
 
    if acao == "inicio":
        mensagens.append(("info", "Campos com * são obrigatórios."))
    else:
        erros = validar(form)
        if erros:
            for erro in erros:
                mensagens.append(("erro", erro))
        else:
            mensagens.append(("ok", "Currículo gerado! Para salvar "
                              "em PDF, aperte Ctrl + P."))
            curriculo = montar_curriculo(form)
 
    marcas = {
        "MENSAGENS": montar_mensagens(mensagens),
        "CURRICULO": curriculo,
    }
    for nome in ["nome", "cargo", "email", "telefone", "cidade",
                 "resumo", "curso", "instituicao", "ano", "exp_titulo",
                 "exp_local", "exp_periodo", "exp_descricao", "outras"]:
        marcas[nome.upper()] = escape(form[nome])
 
    for valor in ["cursando", "concluido"]:
        marcas["MARCAR_" + valor.upper()] = ""
        if form["situacao"] == valor:
            marcas["MARCAR_" + valor.upper()] = "checked"
    for codigo in HABILIDADES:
        marcas["HAB_" + codigo.upper()] = ""
        if codigo in form["habilidades"]:
            marcas["HAB_" + codigo.upper()] = "checked"
    for nivel in NIVEIS_INGLES:
        marcas["ING_" + nivel.upper()] = ""
        if form["ingles"] == nivel:
            marcas["ING_" + nivel.upper()] = "checked"
    for tema in TEMAS:
        marcas["TEMA_" + tema.upper()] = ""
        if form["tema"] == tema:
            marcas["TEMA_" + tema.upper()] = "checked"

    pagina = ler_arquivo("index.html")
    for nome, valor in marcas.items():
        pagina = pagina.replace("{{" + nome + "}}", valor)
    return pagina
 
 
# ---------- 4. Servidor ----------
 
class Atendente(BaseHTTPRequestHandler):
    """Atende cada pedido (requisição) que chega do navegador."""
 
    def do_GET(self):
        caminho = self.path.split("?")[0]
        if caminho == "/":
            form = ler_formulario({})
            pagina = montar_pagina(form, "inicio")
            self.responder(200, "text/html", pagina)
        elif caminho == "/style.css":
            css = ler_arquivo("style.css")
            self.responder(200, "text/css", css)
        else:
            self.responder(404, "text/plain", "Página não encontrada")
    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho).decode("utf-8")
        dados = parse_qs(corpo, keep_blank_values=True)
        acao = campo(dados, "acao")
        if acao == "exemplo":
            form = EXEMPLO.copy()
        else:
            form = ler_formulario(dados)
        pagina = montar_pagina(form, acao)
        self.responder(200, "text/html", pagina)
 
    def responder(self, codigo, tipo, conteudo):
        conteudo = conteudo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo + "; charset=utf-8")
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)
 
 
def conferir_html():
    """Avisa no terminal se faltar alguma marcação no index.html."""
    html = ler_arquivo("index.html")
    faltando = 0
    for marca in ["{{MENSAGENS}}", "{{CURRICULO}}", "{{NOME}}",
                  "{{EMAIL}}", "{{HAB_HTML}}", "{{TEMA_VINHO}}"]:
        if marca not in html:
            print(f"ATENÇÃO: falta {marca} no index.html")
            faltando = faltando + 1
    if faltando == 0:
        print("index.html conferido: marcações encontradas.")
 
 
conferir_html()
servidor = ThreadingHTTPServer(("127.0.0.1", PORTA), Atendente)
print(f"Gerador de Currículo rodando em http://127.0.0.1:{PORTA}")
print("Para parar o servidor, aperte Ctrl + C")
try:
    servidor.serve_forever()
except KeyboardInterrupt:
    print("Servidor encerrado.")


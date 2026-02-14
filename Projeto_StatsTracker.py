from typing import List
from contratos import RegistoEmJogo, EstatisticaChave, ExportavelJSON
import json
import os
import time
from datetime import timedelta
# import da biblioteca rich
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.align import Align

ARQUIVO_DADOS = "dados_equipa.json"

# FUNÇÃO GENÉRICA POLIMÓRFICA (DIP/LSP)
# função é externa a todas as classes, dependendo apenas do contrato ABC.
def obter_totais_marcados(entidades: List[EstatisticaChave]) -> int:
    """Função genérica que usa o polimorfismo para aceder a dados (DIP/LSP)."""
    total = 0
    for e in entidades:
        # Chama o contrato: não se importa se é JogadorDeCampo ou GuardaRedes
        total += e.obter_estatistica_chave("golos")
    return total

class Equipa:
    def __init__(self, nome, vitorias=0, empates=0, derrotas=0, golos_marcados=0, golos_sofridos=0):
        self.nome = nome
        self.jogadores = []          # composição (Equipa contém os seus jogadores)
        self.jogos = []              # composição (Equipa contém os seus jogos)
        self.vitorias = vitorias
        self.empates = empates
        self.derrotas = derrotas
        self.golos_marcados = golos_marcados
        self.golos_sofridos = golos_sofridos

    def adicionar_jogador(self, jogador):
        self.jogadores.append(jogador)

    def adicionar_jogo(self, jogo):
        jogo.definir_resultado()      # deixa o jogo decidir o resultado

        self.jogos.append(jogo)       # guarda o jogo

        # atuliza as estatisticas da equipa com base no resultado do jogo
        if jogo.resultado == "Vitória":
            self.vitorias += 1

        elif jogo.resultado == "Empate":
            self.empates += 1

        elif jogo.resultado == "Derrota":
            self.derrotas += 1

        self.golos_marcados += jogo.golos_marcados
        self.golos_sofridos += jogo.golos_sofridos

    def to_json_dict(self):
        """Converte a equipa para um dicionário, incluindo as listas de jogadores e jogos."""
        return {
            "nome": self.nome,
            "vitorias": self.vitorias,
            "empates": self.empates,
            "derrotas": self.derrotas,
            "golos_marcados": self.golos_marcados,
            "golos_sofridos": self.golos_sofridos,
            "tipo_classe": "Equipa",  # Opcional, mas útil
            # AQUI ESTÁ O TRUQUE: Converter as listas de objetos para listas de dicionários
            "jogadores": [j.to_json_dict() for j in self.jogadores],
            "jogos": [j.to_json_dict() for j in self.jogos]
        }

class Jogador:     # SuperClasse base para herança de JogadorDeCampo e de GuardaRedes
    def __init__(self, nome, numero, posicao, azuis, advertencias, cinco_inicial, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.numero = numero
        self.posicao = posicao
        self.azuis = azuis
        self.advertencias = advertencias
        self.cinco_inicial = cinco_inicial

class JogadorDeCampo(Jogador, ExportavelJSON, RegistoEmJogo, EstatisticaChave):       # herda de jogador e implementa os protocolos (ABCs)
    def __init__(self, nome, numero, posicao, golos=0, assistencias=0, azuis=0, advertencias=0, cinco_inicial=0, plus_minus=0, **kwargs):
        super().__init__(nome=nome, numero=numero, posicao=posicao, azuis=azuis, advertencias=advertencias, cinco_inicial=cinco_inicial, **kwargs)
        self.golos = golos
        self.assistencias = assistencias
        self.azuis = azuis
        self.advertencias = advertencias
        self.cinco_inicial = cinco_inicial
        self.plus_minus = plus_minus

    # Implementação do registo em jogo (OCP/LSP)
    # Este método substitui os antigos def registar_golo() e def fazer_assistencia()
    def processar_evento(self, tipo_evento, **kwargs):
        lista_campo = kwargs.get("jogadores_em_campo")

        if tipo_evento == "golo marcado":
            self.golos += 1

            if lista_campo:
                for j in lista_campo:
                    j.plus_minus += 1
        elif tipo_evento == "assistencia":
            self.assistencias += 1
        # Se futuramente quiser adicionar um novo evento possível (ex: cartão vermelho), a lógica vai aqui.
        elif tipo_evento == "azul":
            self.azuis += 1
        elif tipo_evento == "advertencia":
            self.advertencias += 1
        elif tipo_evento == "5 inicial":
            self.cinco_inicial += 1

    # Implementação do Estatistica Chave (DIP)
    def obter_estatistica_chave(self, chave):
        if chave == "golos":
            return self.golos
        elif chave == "assistencias":
            return self.assistencias
        elif chave == "azuis":
            return self.azuis
        elif chave == "advertencias":
            return self.advertencias
        elif chave == "cinco_inicial":
            return self.cinco_inicial
        return 0

    # Protocolo Informal (DUCK TYPING) para Relatórios (ISP)
    def obter_resumo_estatistico(self):
        return (f"{self.nome} ({self.posicao}) : "
                f"Golos: {self.golos}, "
                f"Assistencias: {self.assistencias}, "
                f"Azuis: {self.azuis}, "
                f"Advertencias: {self.advertencias}"
                f"5 inicial: {self.cinco_inicial}")

    def to_json_dict(self):
        return {
            "tipo_classe": "JogadorDeCampo",
            "nome": self.nome,
            "numero": self.numero,
            "posicao": self.posicao,
            "golos": self.golos,
            "assistencias": self.assistencias,
            "azuis": self.azuis,
            "advertencias": self.advertencias,
            "5 inicial": self.cinco_inicial,
            "plus_minus": self.plus_minus
        }

class GuardaRedes (Jogador, ExportavelJSON, RegistoEmJogo, EstatisticaChave):       # herda de jogador e implementa os protocolos (ABCs)
    def __init__(self, nome, numero, defesas=0, golossofridos=0, bolasparadasdefendidas=0, bolasparadassofridas=0, azuis=0, advertencias=0, cinco_inicial=0, plus_minus=0, **kwargs):
        super().__init__(nome=nome, numero=numero, posicao="Guarda-Redes", azuis=azuis, advertencias=advertencias, cinco_inicial=cinco_inicial, **kwargs)
        self.defesas = defesas
        self.golossofridos = golossofridos
        self.bolasparadasdefendidas = bolasparadasdefendidas
        self.bolasparadassofridas = bolasparadassofridas
        self.azuis = azuis
        self.advertencias = advertencias
        self.cinco_inicial = cinco_inicial
        self.plus_minus = plus_minus

    # Implementação do Registo em Jogo (OCP/LSP)
    # Este método substitiu os antigos def registar_defesa, def registar_golosofrido, def registar_bolaparadadefendida, def registar_bolaparadasofrida
    def processar_evento(self, tipo_evento, **kwargs):
        lista_campo = kwargs.get("jogadores_em_campo")

        if tipo_evento == "golo sofrido":
            self.golossofridos += 1

            if lista_campo:
                for j in lista_campo:
                    j.plus_minus -= 1
        elif tipo_evento == "defesa":
            self.defesas += 1
        elif tipo_evento == "bola parada defendida":
            self.bolasparadasdefendidas += 1
            self.defesas += 1
        elif tipo_evento == "bola parada sofrida":
            self.bolasparadassofridas += 1
            self.golossofridos -= 1

            if lista_campo:
                for j in lista_campo:
                    j.plus_minus -= 1
        elif tipo_evento == "azul":
            self.azuis += 1
        elif tipo_evento == "advertencia":
            self.advertencias += 1
        elif tipo_evento == "5 inicial":
            self.cinco_inicial += 1

    # Implementação do Estatistica Chave (DIP)
    def obter_estatistica_chave(self, chave):
        if chave == "golos sofridos":
            return self.golossofridos
        elif chave == "defesas":
            return self.defesas
        elif chave == "bolas paradas defendidas":
            return self.bolasparadasdefendidas
        elif chave == "bolas paradas sofridas":
            return self.bolasparadassofridas
        elif chave == "azuis":
            return self.azuis
        elif chave == "advertencias":
            return self.advertencias
        elif chave == "cinco inicial":
            return self.cinco_inicial
        elif chave == "golos":
            return 0
        return 0

    # Protocolo Informal (DUCK TYPING) para Relatórios (ISP)
    def obter_resumo_estatistico(self):
        return (f"{self.nome} (Guarda-Redes) : "
                f"Defesas: {self.defesas}, "
                f"Golos Sofridos: {self.golossofridos}, "
                f"Bolas Paradas Defendidas: {self.bolasparadasdefendidas}, "
                f"Bolas Paradas Sofridas: {self.bolasparadassofridas}, "
                f"Azuis : {self.azuis}, "
                f"Advertencias : {self.advertencias}, "
                f"5 Inicial : {self.cinco_inicial}, ")

    def to_json_dict(self):
        return {
            "tipo_classe": "GuardaRedes",
            "nome": self.nome,
            "numero": self.numero,
            "posicao": "Guarda-Redes",
            "defesas": self.defesas,
            "golossofridos": self.golossofridos,
            "bolasparadasdefendidas": self.bolasparadasdefendidas,
            "bolasparadassofridas": self.bolasparadassofridas,
            "azuis": self.azuis,
            "advertencias": self.advertencias,
            "5_inicial": self.cinco_inicial,
            "plus_minus": self.plus_minus
        }

class Evento:      # regista um evento associado a um jogador
    def __init__(self, tipo, jogador, assistente=None):
        self.tipo = tipo              # "golo", "golo sofrido", "defesa", etc
        self.jogador = jogador        # quem executou a ação
        self.assistente = assistente  # opcional

class Jogo:
    def __init__(self, adversario, golos_marcados, golos_sofridos):
        self.adversario = adversario
        self.eventos = []             # composição (o Jogo contém os seus eventos)
        self.golos_marcados = golos_marcados
        self.golos_sofridos = golos_sofridos
        self.resultado = ""

    def adicionar_evento(self, evento):
        self.eventos.append(evento)

        # 1. Atualiza os golos do Jogo (lógica do jogo)
        if evento.tipo == "golo marcado":
            self.golos_marcados += 1
        elif evento.tipo == "golo sofrido":
            self.golos_sofridos += 1

        # 2. Chama o protocolo polimórfico (OCP/LSP)
        # O Jogo apenas precisa de saber que o objeto pode processar o evento.
        evento.jogador.processar_evento(evento.tipo)

        # 3. Trata a assistência (se existir)
        if evento.assistente:
            # Envia um evento específico para o assistente
            evento.assistente.processar_evento("assistencia")

    def definir_resultado(self):
        if self.golos_marcados > self.golos_sofridos:
            self.resultado = "Vitória"
        elif self.golos_marcados == self.golos_sofridos:
            self.resultado = "Empate"
        else:
            self.resultado = "Derrota"

    def to_json_dict(self):
        return {
            "adversario": self.adversario,
            "golos_marcados": self.golos_marcados,
            "golos_sofridos": self.golos_sofridos,
            "resultado": self.resultado
        }

class Estatisticas:
    def __init__(self, equipa):
        self.equipa = equipa

    def calcular_totais(self):
        total_golos_marcados = sum(jogo.golos_marcados for jogo in self.equipa.jogos)
        total_golos_sofridos = sum(jogo.golos_sofridos for jogo in self.equipa.jogos)
        return total_golos_marcados, total_golos_sofridos

    def jogadores_em_destaque(self):
        # 1. Filtra APENAS pelos Jogadores de Campo
        # Usa o 'isinstance' para garantir que só consideramos quem faz golos/assistências
        jogadores_campo = [
            j for j in self.equipa.jogadores
            if isinstance(j, JogadorDeCampo)
        ]

        if not jogadores_campo:
            return None, None

        # 2. Encontra o melhor marcador e assistente usando o protocolo (DIP)
        # O melhor marcador e assistente devem ser encontrados entre aqueles com golos/assistências > 0

        # Filtrar para evitar que a função max() falhe se a lista estiver vazia
        jogadores_com_golos = [j for j in jogadores_campo if j.obter_estatistica_chave("golos") > 0]
        jogadores_com_assist = [j for j in jogadores_campo if j.obter_estatistica_chave("assistencias") > 0]
        jogadores_com_azuis = [j for j in jogadores_campo if j.obter_estatistica_chave("azuis") > 0]
        jogadores_com_advertencias = [j for j in jogadores_campo if j.obter_estatistica_chave("advertencias") > 0]

        melhor_marcador = None
        melhor_assistente = None
        mais_azuis = None
        mais_advertencias = None

        if jogadores_com_golos:
            melhor_marcador = max(jogadores_com_golos, key=lambda j: j.obter_estatistica_chave("golos"))

        if jogadores_com_assist:
            melhor_assistente = max(jogadores_com_assist, key=lambda j: j.obter_estatistica_chave("assistencias"))

        if jogadores_com_azuis:
            mais_azuis = max(jogadores_com_azuis, key=lambda j: j.obter_estatistica_chave("azuis"))

        if jogadores_com_advertencias:
            mais_advertencias = max(jogadores_com_advertencias, key=lambda j: j.obter_estatistica_chave("advertencias"))

        return melhor_marcador, melhor_assistente, mais_azuis, mais_advertencias

class Relatorios:
    def __init__(self, equipa):
        self.equipa = equipa   #recebe o objeto Equipa para aceder aos dados
        self.estat = Estatisticas(equipa)  # composição

    def estatisticas_equipa(self):
        total_golos_marcados, total_golos_sofridos = self.estat.calcular_totais()
        print(f"\n==== Estatísticas da Equipa: {self.equipa.nome} ====")
        print(f"Vitórias : {self.equipa.vitorias}")
        print(f"Empates : {self.equipa.empates}")
        print(f"Derrotas : {self.equipa.derrotas}")
        print(f"Golos marcados : {total_golos_marcados}")
        print(f"Golos sofridos : {total_golos_sofridos}")

    def estatisticas_jogadores(self):
        print(f"\n==== Estatísticas Individuais ====")
        """Usa o protocolo informal 'obter_resumo_estatistico' (ISP/Duck Typing)."""
        sumarios = []
        for j in self.equipa.jogadores:  # Acede via Equipa (Lógica Original)
            # Verifica o protocolo, conforme a Decisão Polimórfica da AF5.1
            if hasattr(j, 'obter_resumo_estatistico'):
                resumo = j.obter_resumo_estatistico()
                sumarios.append(resumo)
                print(resumo)

        melhor_marcador, melhor_assistente, mais_azuis, mais_advertencias = self.estat.jogadores_em_destaque()

        if melhor_marcador and melhor_assistente and mais_azuis:
            print(
                f"\nMelhor marcador : {melhor_marcador.nome} ({melhor_marcador.obter_estatistica_chave('golos')} golos)")
            print(
                f"Melhor assistente : {melhor_assistente.nome} ({melhor_assistente.obter_estatistica_chave('assistencias')} assistências)")
            print(
                f"Jogador com mais azuis : {mais_azuis.nome} ({mais_azuis.obter_estatistica_chave('azuis')} azuis)")
        else:
            print("\nNão há jogadores de campo com estatísticas para destaque.")

        return sumarios # return fica no final, caso seja preciso para testes

# Carregar e salvar dados
def criar_plantel():
    """Cria a lista inicial se não houver ficheiro."""
    lista = [
        GuardaRedes("Toni Mendonça", 27),
        GuardaRedes("Kiko Fernandes", 47),
        JogadorDeCampo("Zé Tiago", 3, "Médio"),
        JogadorDeCampo("Tiago Duarte", 4, "Defesa"),
        JogadorDeCampo("Pákito", 7, "Avançado"),
        JogadorDeCampo("Pedro Lopes", 74, "Avançado"),
        JogadorDeCampo("Diogo Pernas", 77, "Médio"),
        JogadorDeCampo("Manuel Correia", 84, "Defesa"),
        JogadorDeCampo("Jotta", 87, "Defesa"),
        JogadorDeCampo("Bernardo Ramalho", 88, "Avançado")
    ]
    return lista

def carregar_dados():
    """Lê o JSON e recria os objetos Equipa e Jogadores"""
    equipa = Equipa("Parede FC")

    if not os.path.exists(ARQUIVO_DADOS):
        # Se não existir o ficheiro, carrega os jogadores "padrão"
        jogadores_padrao = criar_plantel()
        for j in jogadores_padrao:
            equipa.adicionar_jogador(j)
        return equipa

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            dados = json.load(f)

            # 1. carregar stats da Equipa
            equipa.vitorias = dados.get("vitorias", 0)
            equipa.empates = dados.get("empates", 0)
            equipa.derrotas = dados.get("derrotas", 0)
            equipa.golos_marcados = dados.get("golos_marcados", 0)
            equipa.golos_sofridos = dados.get("golos_sofridos", 0)

            # 2. carregar Jogadores
            plantel_dados = dados.get("jogadores", dados.get("plantel", []))

            for p_dados in plantel_dados:
                tipo = p_dados.get("tipo_classe")
                jogador = None

                # instanciar a classe correta com base no tipo guardado
                if tipo == "GuardaRedes" or p_dados.get("posicao") in ["Guarda-Redes", "GR"]:
                    jogador = GuardaRedes(
                        nome=p_dados["nome"],
                        numero=p_dados["numero"],
                        defesas=p_dados.get("defesas", 0),
                        golossofridos=p_dados.get("golossofridos", 0),
                        bolasparadasdefendidas=p_dados.get("bolasparadasdefendidas", 0),
                        bolasparadassofridas=p_dados.get("bolasparadassofridas", 0),
                        azuis=p_dados.get("azuis", 0),
                        advertencias=p_dados.get("advertencias", 0),
                        cinco_inicial=p_dados.get("5 inicial", 0),
                        plus_minus=p_dados.get("plus_minus", 0),
                    )
                else: # JogadorDeCampo
                    jogador = JogadorDeCampo(
                        nome=p_dados["nome"],
                        numero=p_dados["numero"],
                        posicao=p_dados["posicao"],
                        golos=p_dados.get("golos", 0),
                        assistencias=p_dados.get("assistencias", 0),
                        azuis=p_dados.get("azuis", 0),
                        advertencias=p_dados.get("advertencias", 0),
                        cinco_inicial=p_dados.get("5_inicial", 0),
                        plus_minus=p_dados.get("plus_minus", 0),
                    )

                if jogador:
                    equipa.adicionar_jogador(jogador)

            # --- 3. RECUPERAR LISTA DE JOGOS ---
            # Vamos ler a lista "jogos" do JSON e voltar a criar objetos Jogo
            lista_jogos_antigos = dados.get("jogos", [])

            for j_dados in lista_jogos_antigos:
                # 1. Recria o jogo com os dados do ficheiro
                jogo_guardado = Jogo(
                    adversario=j_dados["adversario"],
                    golos_marcados=j_dados["golos_marcados"],
                    golos_sofridos=j_dados["golos_sofridos"]
                )
                # 2. Define o resultado que já estava calculado
                jogo_guardado.resultado = j_dados.get("resultado", "")

                # 3. Adiciona à lista da equipa SEM alterar as vitórias/derrotas
                equipa.jogos.append(jogo_guardado)

        return equipa

    except Exception as e:
                print(f"Erro ao carregar JSON: {e}. A criar nova equipa.")
                return equipa

def salvar_dados(equipa):
            """Guarda o estado completo da equipa e jogadores."""
            with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
                # o método to_json_dict da Equipa já trata de tudo
                json.dump(equipa.to_json_dict(), f, indent=4, ensure_ascii=False)
            print("Dados guardados em 'dados_parede_fc.json'.")

# classe responsável por mostrar os dados bem organizados usando a biblioteca rich
class InterfaceVisual:
    def __init__(self):
        self.console = Console(force_terminal=True)

    def mostrar_tabela_jogadores(self, equipa):
        """cria uma tabela formatada com as stats dos jogadores."""
        # 1º tabela para os guarda redes. Cria a tabela com título e bordas arredondadas
        table_gr = Table(title=f"Guarda-Redes do {equipa.nome}", box=box.ROUNDED)

        # colunas específicas de GR
        table_gr.add_column("Nº", style="cyan", justify="right")
        table_gr.add_column("Nome", style="magenta")
        table_gr.add_column("Defesas", justify="center", style="green")
        table_gr.add_column("Golos Sofridos", justify="center", style="red")
        table_gr.add_column("Bolas Paradas Defendidas", justify="center")
        table_gr.add_column("Bolas Paradas Sofridas", justify="center")
        table_gr.add_column("Titular", justify="center")
        table_gr.add_column("Azuis", justify="center", style="blue")
        table_gr.add_column("Advertências", justify="center", style="yellow")

        # 2ª tabelas para os jogadores de campo
        table_campo = Table(title=f"Jogadores de Campo do {equipa.nome}:", box=box.ROUNDED)

        # definir as colunas
        table_campo.add_column("Nº", justify="right", style="cyan")
        table_campo.add_column("Nome", style="magenta")
        table_campo.add_column("Posição", style="green")
        table_campo.add_column("Golos", justify="center", style="green")
        table_campo.add_column("Assistências", justify="center", style="red")
        table_campo.add_column("Titular", justify="center")
        table_campo.add_column("Azuis", justify="center", style="blue")
        table_campo.add_column("Advertencias", justify="center" ,style="yellow")
        table_campo.add_column("+/-", justify="center", style="bold cyan")

        # separar os jogadores e preencher as tabelas
        tem_gr = False
        tem_campo = False

        for jogador in equipa.jogadores:
            try:
                titularidade = int(jogador.cinco_inicial)
            except (ValueError, TypeError):
                titularidade = 0

            azuis = str(getattr(jogador, 'azuis', 0))
            advertencias = str(getattr(jogador, 'advertencias', 0))
            cinco = str(titularidade)

            # lógica para detetar se é GR (verifica a posição ou a classe)
            if jogador.posicao == "Guarda-Redes" or "GuardaRedes" in str(type(jogador)):
                tem_gr = True
                table_gr.add_row(
                    str(jogador.numero),
                    jogador.nome,
                    str(getattr(jogador, "defesas", 0)),
                    str(getattr(jogador, "golossofridos", 0)),
                    str(getattr(jogador, "bolasparadasdefendidas", 0)),
                    str(getattr(jogador, "bolasparadassofridas", 0)),
                    cinco,
                    azuis,
                    advertencias,
                )
            else:
                tem_campo = True
                table_campo.add_row(
                    str(jogador.numero),
                    jogador.nome,
                    jogador.posicao,
                    str(getattr(jogador, "golos", 0)),
                    str(getattr(jogador, "assistencias", 0)),
                    cinco,
                    azuis,
                    advertencias,
                    str(getattr(jogador, "plus_minus", 0))
                )

                # imprime as tabelas (se houver jogadores desse tipo)
        if tem_gr:
            self.console.print(table_gr)
            print("\n")  # espaço visual

        if tem_campo:
            self.console.print(table_campo)

    def selecionar_jogador(self, lista_jogadores, filtro_posicao=None, mensagem="Selecione o jogador"):

        table = Table(title=mensagem, box=box.SIMPLE_HEAD)
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Nome", style="magenta")
        table.add_column("Posição", style="green")

        # lista temporária para guardar quem pode ser escolhido
        jogadores_validos = []

        # preencher a tabela
        for i, jogador in enumerate(lista_jogadores, 1):
            # se houver filtro (ex: Guarda-Redes), só mostra esses
            if filtro_posicao is None or jogador.posicao == filtro_posicao:
                table.add_row(str(i), jogador.nome, jogador.posicao)
                jogadores_validos.append(i)

        self.console.print(table)

        # loop para garantir que se escolhe um número valido
        while True:
            opcao = Prompt.ask(f"[bold yellow]Digite o ID (ou 0 para cancelar)[/]")

            try:
                escolha = int(opcao)
                if escolha == 0:
                    return None

                if escolha in jogadores_validos:
                    # retorna o objeto jogador correspondente (indice = escolha - 1, pois em pyhon os indices começam em 0)
                    return lista_jogadores[escolha - 1]
                else:
                    self.console.print("[red]ID inválido. Escolha um da lista acima.[/red]")
            except ValueError:
                self.console.print("[red]Por favor digite um número.[/red]")

    def mostrar_historico_jogos(self, equipa):
        """cria uma tabela com o historico de resultados"""
        if not equipa.jogos:
            self.console.print("\n[bold red]Ainda não há jogos registados![/bold red]")
            return

        table = Table(title="Historico de Jogos", box=box.DOUBLE_EDGE)

        table.add_column("Jogo", justify="right")
        table.add_column("Resultado", justify="center", style="white")
        table.add_column("Resultado (V,E,D)", justify="center")
        table.add_column("Placar", justify="center")

        for i, jogo in enumerate(equipa.jogos, 1):
            cor_resultado = "white"
            if jogo.resultado == "Vitória":
                cor_resultado = "green"
            elif jogo.resultado == "Empate":
                cor_resultado = "yellow"
            elif jogo.resultado == "Derrota":
                cor_resultado = "red"

            resultado_formatado = f"[{cor_resultado}]{jogo.resultado}[/{cor_resultado}]"
            placar = f"{jogo.golos_marcados} - {jogo.golos_sofridos}"

            table.add_row(str(i), jogo.adversario, resultado_formatado, placar)

        self.console.print(table)

    def mostrar_lista_jogadores(self, equipa):
        """mostra apenas os jogadores com id para consulta"""
        tabela = Table(title="Plantel", box=box.SIMPLE_HEAD)
        tabela.add_column("ID", style="cyan", justify="right")
        tabela.add_column("Nome", style="cyan", justify="right")

        for i, jogador in enumerate(equipa.jogadores, 1):
            tabela.add_row(str(i), jogador.nome)

        self.console.print(tabela)

# opções do menu interativo
def escolher_jogador_menu(equipa, posicao_filtro=None):
    """Lista os jogadores enumerados e pede ao utilizador para escolher pelo número."""

    # 1. Filtrar a lista de jogadores (Todos ou só GR)
    lista_selecao = []
    if posicao_filtro == "Guarda-Redes":
        # Cria uma lista apenas com quem tem a posição "Guarda-Redes"
        lista_selecao = [j for j in equipa.jogadores if j.posicao == "Guarda-Redes"]
    else:
        # Usa a lista completa
        lista_selecao = equipa.jogadores

    # Se não houver ninguém (ex: filtro Guarda-Redes mas não há Guarda-Redes na equipa)
    if not lista_selecao:
        print("❌ Nenhum jogador encontrado para esta seleção.")
        return None

    # 2. Mostrar a lista enumerada (1. Nome, 2. Nome...)
    print("\n--- LISTA DE JOGADORES ---")
    for i, jogador in enumerate(lista_selecao, 1):
        print(f"{i}. {jogador.nome} ({jogador.posicao})")

    # 3. Pedir ao utilizador para escolher o número
    while True:
        try:
            escolha = int(input(f"Escolha o número (1-{len(lista_selecao)}) ou 0 para cancelar: "))

            if escolha == 0:
                return None

            if 1 <= escolha <= len(lista_selecao):
                # Retorna o JOGADOR correspondente ao número escolhido
                # (indice é escolha - 1 porque listas começam em 0)
                return lista_selecao[escolha - 1]
            else:
                print("Número inválido.")
        except ValueError:
            print("Por favor, insira um número válido.")

def obter_tempo_atual():
    # tempo decorrido em segundos
    decorrido = time.time() - tempo_inicio - tempo_pausado
    return str(timedelta(seconds=int(decorrido)))[2:]     # retorna MM:SS


def menu_comecar_jogo(equipa):
    # instanciar a classe visual
    visual = InterfaceVisual()

    os.system('cls' if os.name == 'nt' else 'clear')      # limpa o ecra
    visual.console.print(Panel("[bold white]CONFIGURAÇÃO DO JOGO[/]", style="blue"))
    adversario = Prompt.ask("Nome do adversário").upper()

    # definir 5 inicial
    os.system('cls' if os.name == 'nt' else 'clear')      # limpa o ecra

    visual.mostrar_lista_jogadores(equipa)
    visual.console.print("\n[bold]Definição do 5 inicial[/bold]")
    cincoinicial = Prompt.ask("Digite os IDs dos titulares separados por vírgula (ex: 1, 2, 3, 4, 5)")

    jogadores_em_campo = []

    if cincoinicial.strip():
        ids = [int(x.strip()) for x in cincoinicial.split(",")]
        for idx in ids:
            if 1 <= idx <= len(equipa.jogadores):
                jogador = equipa.jogadores[idx - 1]
                jogador.processar_evento("5 inicial")
                jogadores_em_campo.append(jogador)

    # loop do jogo
    golos_nos = 0
    golos_adversario = 0

    faltas_nos = 0
    faltas_adversario = 0

    parte_atual = 1
    tempo_inicio = time.time()    # guarda o momento exato em que o jogo começou
    tempo_pausado = 0
    tempo_congelado = False       # para saber se o relógio parou
    momento_azul = None           # para controlar o tempo de exclusão

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        segundos = int(time.time() - tempo_inicio)

        # verificar se chegou aos 25 min (1500 segundos)
        aviso_status = ""

        if segundos >= 1500:
            tempo_congelado = True

            if parte_atual == 1:
                segundos = 1500     # fixa visualmente nos 25 min
                aviso_status = "[Intervalo - Inicie a 2º Parte]"

            else:
                segundos = 1500     # fixa visualmente nos 50  min
                aviso_status = " [Fim de Jogo] "

        else:
            tempo_congelado = False

        tempo_jogo = str(timedelta(seconds=segundos))
        if segundos < 3600:
            tempo_jogo = tempo_jogo[2:]      # remove a hora

        # placar do jogo
        texto_placar = (
            f"[bold red]PAREDE FC[/] {golos_nos} - {golos_adversario} [bold white]{adversario}[/]\n"
            f"[[bold yellow]{parte_atual}ª PARTE | {tempo_jogo}{aviso_status}[/]"
        )
        visual.console.print(Panel(Align.center(texto_placar), style="blue"))

        visual.console.print("1. Golo do Parede FC")
        visual.console.print("2. Golo Sofrido (inclui bola parada)")
        visual.console.print("3. Defesa GR (remate ou bola parada)")
        visual.console.print("4. Cartões (azul ou advertências)")
        visual.console.print("5. Substituição")
        visual.console.print("6. Fim do underplay")
        visual.console.print("7. Falta")
        visual.console.print("8. Inicio 2ª Parte")
        visual.console.print("0. Terminar Jogo")

        op = Prompt.ask("Opção", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])

        if op == "1":
            # reutilização da classe visual aqui
            marcador = visual.selecionar_jogador(jogadores_em_campo, mensagem="Quem marcou?")

            if marcador:
                marcador.processar_evento("golo marcado", jogadores_em_campo=jogadores_em_campo)
                golos_nos += 1
                visual.console.print(f"[green]Golo de {marcador.nome}![/green]")

                if Prompt.ask("Houve assistência?", choices=["s", "n"]) == "s":
                    assistente = visual.selecionar_jogador(jogadores_em_campo, mensagem="Quem assistiu?")
                    if assistente:
                        assistente.processar_evento("assistencia")

            input("Enter para continuar...")

        elif op == "2":
            golos_adversario += 1
            # filtrar só GRs automaticamente
            gr = visual.selecionar_jogador(equipa.jogadores, filtro_posicao="Guarda-Redes", mensagem="Quem sofreu?")
            if gr:
                if Prompt.ask("Bola parada?", choices=["s", "n"]) == "s":
                    gr.processar_evento("bola parada sofrida", jogadores_em_campo=jogadores_em_campo)
                else:
                    gr.processar_evento("golo sofrido", jogadores_em_campo=jogadores_em_campo)
            input("Enter para continuar...")

        elif op == "3":
            # filtra só GRs automaticamente
            gr = visual.selecionar_jogador(equipa.jogadores, filtro_posicao="Guarda-Redes", mensagem="Quem defendeu?")
            if gr:
                if Prompt.ask("Bola parada?", choices=["s", "n"]) == "s":
                    gr.processar_evento("bola parada defendida")
                else:
                    gr.processar_evento("defesa")
            input("Enter para continuar...")

        elif op == "4":
            infrator = visual.selecionar_jogador(equipa.jogadores, mensagem="Quem levou cartão?")
            if infrator in jogadores_em_campo:
                tipo = Prompt.ask("Tipo", choices=["azul", "advertencia"])
                if tipo == "azul":
                    infrator.processar_evento("azul")
                    jogadores_em_campo.remove(infrator)
                    momento_azul = time.time()

                    visual.console.print(f"\n[bold blue] UnderPlay de 2 min iniciado! O {infrator.nome} levou cartão azul.")
                    visual.console.print(f"[bold red] A equipa está a jogar com {len(jogadores_em_campo)}")

                else:
                    amarelos_jogo = getattr(infrator, "amarelos_neste_jogo", 0)    # verifica se o jogador ja tem o contador, se não tiver cria-o a 0
                    infrator.amarelos_neste_jogo = amarelos_jogo + 1

                    infrator.processar_evento("advertencia")

                    if infrator.amarelos_neste_jogo >= 2:
                        visual.console.print(f"[bold blue] Segunda advertência = azul,  jogador tem de sair de campo")
                        infrator.processar_evento("azul")
                        jogadores_em_campo.remove(infrator)

                    else:
                        visual.console.print(f"[yellow] {infrator.nome} levou a primeira advertencia.")
            else:
                tipo = Prompt.ask("Tipo", choices=["azul", "advertencia"])
                if tipo == "azul":
                    infrator.processar_evento("azul")
                    visual.console.print("[yellow] O jogador está no banco, precisa tirar um jogador para sair de campo. ")
                    visual.console.print("Quem vai [red]SAIR[/]?")
                    for i, j in enumerate(jogadores_em_campo):
                        print(f"{i + 1}. {j.nome} ({j.numero})")

                    sai_idx = IntPrompt.ask("Escolha o nº da lista acima") - 1

                    if 0 <= sai_idx < len(jogadores_em_campo):
                        jogador_que_sai = jogadores_em_campo[sai_idx]
                else:
                    amarelos_jogo = getattr(infrator, "amarelos_neste_jogo",
                                            0)  # verifica se o jogador ja tem o contador, se não tiver cria-o a 0
                    infrator.amarelos_neste_jogo = amarelos_jogo + 1

                    infrator.processar_evento("advertencia")

                    if infrator.amarelos_neste_jogo >= 2:
                        visual.console.print(f"[bold blue] Segunda advertência = azul,  jogador tem de sair de campo")
                        infrator.processar_evento("azul")

                        visual.console.print("[yellow] O jogador está no banco, precisa tirar um jogador para sair de campo. ")
                        visual.console.print("Quem vai [red]SAIR[/]?")
                        for i, j in enumerate(jogadores_em_campo):
                            print(f"{i + 1}. {j.nome} ({j.numero})")

                        sai_idx = IntPrompt.ask("Escolha o nº da lista acima") - 1

                        if 0 <= sai_idx < len(jogadores_em_campo):
                            jogador_que_sai = jogadores_em_campo[sai_idx]
                    else:
                        infrator.processar_evento("advertencia")
                        visual.console.print(f"[yellow] {infrator.nome} levou a primeira advertencia.")

            input("Enter para continuar...")

        elif op == "5":
            visual.console.print("\n[bold yellow]--- SUBSTITUIÇÃO ---[/]")

            # 1. Escolher quem SAI
            visual.console.print("Quem vai [red]SAIR[/]?")
            for i, j in enumerate(jogadores_em_campo):
                print(f"{i + 1}. {j.nome} ({j.numero})")

            sai_idx = IntPrompt.ask("Escolha o nº da lista acima") - 1

            if 0 <= sai_idx < len(jogadores_em_campo):
                jogador_que_sai = jogadores_em_campo[sai_idx]

                # 2. Escolher quem ENTRA
                # Mostrar apenas quem NÃO está em campo (Banco)
                banco = [j for j in equipa.jogadores if j not in jogadores_em_campo]

                visual.console.print(f"\nQuem vai [green]ENTRAR[/] para o lugar de {jogador_que_sai.nome}?")
                for i, j in enumerate(banco):
                    print(f"{i + 1}. {j.nome} ({j.numero})")

                entra_idx = IntPrompt.ask("Escolha o nº da lista do banco") - 1

                if 0 <= entra_idx < len(banco):
                    jogador_que_entra = banco[entra_idx]

                    # TROCA NA LISTA
                    jogadores_em_campo.remove(jogador_que_sai)
                    jogadores_em_campo.append(jogador_que_entra)

                    visual.console.print(f"[green]🔄 Substituição feita: Sai {jogador_que_sai.nome}, Entra {jogador_que_entra.nome}[/]")
                else:
                    print("Opção de banco inválida.")
            else:
                print("Opção de campo inválida.")

        elif op == "6":
            # bloco de verificação de tempo
            permitir_entrada = True

            # verifica se existe cartão azul ativo e se passaram 120 segundos (2 min)
            if momento_azul is not None:
                tempo_passado = time.time() - momento_azul

                if tempo_passado < 120:
                    faltam = 120 - int(tempo_passado)
                    visual.console.print(f"\n[bold blue] Ainda faltam {faltam} segundos para o fim do underplay.")
                    permitir_entrada = False
                else:
                    momento_azul = None    # tempo ja passou

            if permitir_entrada:
                qtd_em_campo = len(jogadores_em_campo)

                if qtd_em_campo >= 5:
                    visual.console.print("[red]A equipa já está completa (5 jogadores)![/]")
                else:
                    visual.console.print(f"\n[green]⚡ Fim do underplay [/]")

                    # Mostrar quem está no banco
                    banco = [j for j in equipa.jogadores if j not in jogadores_em_campo]

                    for i, j in enumerate(banco):
                        print(f"{i + 1}. {j.nome} ({j.numero})")

                    idx = IntPrompt.ask("Quem vai entrar?") - 1

                    if 0 <= idx < len(banco):
                        novo_jogador = banco[idx]
                        jogadores_em_campo.append(novo_jogador)
                        visual.console.print(
                            f"[bold green]✅ {novo_jogador.nome} entrou! A equipa joga agora com {len(jogadores_em_campo)}.[/]")
                    else:
                        print("Opção inválida.")

        elif op == "7":
            visual.console.print("Falta de equipa")

            falta_quem = Prompt.ask("Quem fez falta?", choices=["Parede FC", "Adversário"])
            if falta_quem == "Parede FC":
                faltas_nos +=1
                if faltas_nos >= 10 and (faltas_nos % 5 == 0):    # se for maior ou igual a 10 e o resto da divisaõ por 5 for 0 (15,20,25...)
                    visual.console.print(Panel(f"{faltas_nos} Falta! Livre direto."))
                    gr_em_campo = None
                    for j in jogadores_em_campo:
                        if hasattr(j, "defesas"):
                            gr_em_campo = j
                            break

                    if not gr_em_campo:
                        gr_em_campo = visual.selecionar_jogador(equipa, mensagem="Quem é o guarda-redes a defender?")

                    if gr_em_campo:
                        visual.console.print(f"[bold]{gr_em_campo.nome} está na baliza para defender a bola parada.[/]")
                        resultado = Prompt.ask("Golo?", choices=["sim", "não"])

                        if resultado == "não":
                            gr_em_campo.processar_evento("defesa")
                            gr_em_campo.processar_evento("bola parada defendida")

                        else: # golo sofrido
                            gr_em_campo.processar_evento("golo sofrido")
                            gr_em_campo.processar_evento("bola parada sofrida")

                            golos_adversario += 1

                            visual.console.print(f"[red] Golo sofrido de bola parada.[/]")
            else:
                faltas_adversario +=1
                if faltas_adversario >= 10 and (faltas_adversario % 5 == 0):    # se for maior ou igual a 10 e o resto da divisaõ por 5 for 0 (15,20,25...)
                    visual.console.print(Panel(f"{faltas_adversario} Falta! Livre direto."))

        elif op == "8":
            if parte_atual == 1:
                if tempo_congelado:
                    visual.console.print("[green]Intervalo terminado! A começar a 2ª Parte")
                else:
                    confirmar = Prompt.ask("O tempo ainda não acabou. Forçar 2ª Parte?", choices=["s", "n"])
                    if confirmar == "n":
                        continue    # voltar ao menu sem fazer nada
                # mudança de parte
                parte_atual = 2
                inicio_parte = time.time()      # reset ao relógio
                momento_azul = None

            else:
                visual.console.print("[red]Já estás na 2ª Parte![/]")
                time.sleep(1)

        elif op == "0":
            novo_jogo = Jogo(adversario, golos_nos, golos_adversario)

            novo_jogo.definir_resultado()

            equipa.adicionar_jogo(novo_jogo)

            salvar_dados(equipa)
            break

def menu_estatisticas(equipa):
    # ativar rich
    visual = InterfaceVisual()

    # cabeçalho geral
    visual.console.print(f"\n[bold underline]=== Estatisticas da Equipa {equipa.nome} ===")
    print(f"Vitórias : {equipa.vitorias}")
    print(f"Empates : {equipa.empates}")
    print(f"Derrotas : {equipa.derrotas}")
    print(f"Golos Marcados : {equipa.golos_marcados}")
    print(f"Golos Sofridos : {equipa.golos_sofridos}")

    print("\n")

    # chamar as tabelas rich
    visual.mostrar_tabela_jogadores(equipa)

    print("\n")
    visual.mostrar_historico_jogos(equipa)

    # pausa para ler antes de sair
    input("\nPressione <enter> para voltar.")

def menu_relatorios(equipa):
    print("\n" + "=" * 30)
    print("     RELATÓRIOS DE AUDITORIA    ")
    print("=" * 30)
    print("Histórico cronológico de ações registadas:")
    encontrou_logs = False
    for j in equipa.jogadores:
        if j.historico_logs:
            encontrou_logs = True
            print(f"\n--- {j.nome} ---")
            for log in j.historico_logs:
                print(log)

    if not encontrou_logs:
        print("Ainda não há eventos registados.")
    input("\nPressione ENTER para voltar...")

# menu principal
def main():
    equipa = carregar_dados()
    console = Console()     # instancia a consola da biblioteca Rich

    while True:
        # limpar o ecrã para dar aspeto de "App"
        os.system('cls' if os.name == 'nt' else 'clear')

        # criar o texto do menu com formatação Rich
        texto_menu = (
            "[bold green]1.[/bold green] Começar Jogo (Registar Eventos)\n"
            "[bold cyan]2.[/bold cyan] Ver Estatísticas (Tabelas)\n"
            "[bold yellow]3.[/bold yellow] Relatórios (Auditoria)\n"
            "[bold red]0.[/bold red] Sair e Guardar"
        )

        # criar um painel
        painel_menu = Panel(
            Align.center(texto_menu),
            title="[bold white]PAREDE FC STATS TRACKER[/bold white]",
            subtitle="Escolha uma opção",
            box=box.ROUNDED,
            padding=(1, 2),      # espaçamento interno
            width=50            # largura fixa
        )

        # mostrar o painel
        console.print("\n")
        console.print(Align.center(painel_menu))
        console.print("\n")

        # pedir a opção
        # choices = ["0", "1", "2", "3"] obriga o utilizador a escolher uma destas opções
        opcao = Prompt.ask(
            "[bold magenta] Digite a sua opção[/bold magenta]",
            choices=["0", "1", "2", "3"],
        )

        if opcao == "1":
            menu_comecar_jogo(equipa)
        elif opcao == "2":
            menu_estatisticas(equipa)
        elif opcao == "3":
            menu_relatorios(equipa)
        elif opcao == "0":
            salvar_dados(equipa)
            console.print("[bold green]Dados guardados com sucesso. Até à próxima![/bold green]")
            break
        else:
            input("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()


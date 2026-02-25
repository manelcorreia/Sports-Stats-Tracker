from typing import List
from contratos import RegistoEmJogo, EstatisticaChave, ExportavelJSON
import json
import os
import time
from datetime import timedelta

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
    def __init__(self, nome, numero, posicao, azuis, advertencias, cinco_inicial, faltas=0, perdas_posse=0, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.numero = numero
        self.posicao = posicao
        self.azuis = azuis
        self.advertencias = advertencias
        self.cinco_inicial = cinco_inicial
        self.faltas = faltas
        self.perdas_posse = perdas_posse

class JogadorDeCampo(Jogador, ExportavelJSON, RegistoEmJogo, EstatisticaChave):       # herda de jogador e implementa os protocolos (ABCs)
    def __init__(self, nome, numero, posicao, golos=0, assistencias=0, azuis=0, advertencias=0, cinco_inicial=0, plus_minus=0, faltas=0, perdas_posse=0, **kwargs):
        super().__init__(nome=nome, numero=numero, posicao=posicao, azuis=azuis, advertencias=advertencias, cinco_inicial=cinco_inicial, faltas=faltas, perdas_posse=perdas_posse, **kwargs)
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
        elif tipo_evento == "falta":
            self.faltas += 1
        elif tipo_evento == "perda posse":
            self.perdas_posse += 1

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
        elif chave == "faltas":
            return self.faltas
        elif chave == "perdas_posse":
            return self.perdas_posse
        return 0

    # Protocolo Informal (DUCK TYPING) para Relatórios (ISP)
    def obter_resumo_estatistico(self):
        return (f"{self.nome} ({self.posicao}) : "
                f"Golos: {self.golos}, "
                f"Assistencias: {self.assistencias}, "
                f"Azuis: {self.azuis}, "
                f"Advertencias: {self.advertencias}, "
                f"5 inicial: {self.cinco_inicial}, "
                f"Plus_minus: {self.plus_minus}, "
                f"Faltas: {self.faltas}, "
                f"Perdas_posse: {self.perdas_posse}")

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
            "plus_minus": self.plus_minus,
            "faltas": self.faltas,
            "perdas_posse": self.perdas_posse
        }

class GuardaRedes (Jogador, ExportavelJSON, RegistoEmJogo, EstatisticaChave):       # herda de jogador e implementa os protocolos (ABCs)
    def __init__(self, nome, numero, defesas=0, golossofridos=0, bolasparadasdefendidas=0, bolasparadassofridas=0, azuis=0, advertencias=0, cinco_inicial=0, plus_minus=0, faltas=0, **kwargs):
        super().__init__(nome=nome, numero=numero, posicao="Guarda-Redes", azuis=azuis, advertencias=advertencias, cinco_inicial=cinco_inicial, faltas=faltas, **kwargs)
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
        elif tipo_evento == "falta":
            self.faltas += 1

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
        elif chave == "faltas":
            return self.faltas
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
                f"5 Inicial : {self.cinco_inicial}, "
                f"Faltas : {self.faltas}")

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
            "plus_minus": self.plus_minus,
            "faltas": self.faltas
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
                        faltas=p_dados.get("faltas", 0)
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
                        faltas=p_dados.get("faltas", 0),
                        perdas_posse=p_dados.get("perdas_posse", 0)
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


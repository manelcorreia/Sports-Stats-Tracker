import streamlit as st
import pandas as pd
import time
from datetime import timedelta


# --- IMPORTA AS TUAS CLASSES ---
try:
    from Projeto_StatsTracker import carregar_dados, salvar_dados, Jogo
except ImportError:
    st.error("Erro: O ficheiro 'Projeto_StatsTracker.py' não está na mesma pasta.")
    carregar_dados = salvar_dados = Jogo = None
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Parede FC Live", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .score-board { 
        background-color: #0e1117; 
        padding: 15px; 
        border-radius: 10px; 
        border: 2px solid #333; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    /* Aumentar o tamanho dos emojis nos botões */
    button p { font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTÃO DE ESTADO (SESSION STATE) ---
if 'equipa' not in st.session_state: st.session_state.equipa = carregar_dados()
if 'fase' not in st.session_state: st.session_state.fase = "menu"

# Variáveis de Jogo
if 'jogadores_em_campo' not in st.session_state: st.session_state.jogadores_em_campo = []
if 'adversario' not in st.session_state: st.session_state.adversario = "Visitante"
if 'cronometro_inicio' not in st.session_state: st.session_state.cronometro_inicio = None
if 'tempo_acumulado' not in st.session_state: st.session_state.tempo_acumulado = 0
if 'cronometro_correndo' not in st.session_state: st.session_state.cronometro_correndo = False
if 'golos_nos' not in st.session_state: st.session_state.golos_nos = 0
if 'golos_adv' not in st.session_state: st.session_state.golos_adv = 0
if 'parte' not in st.session_state: st.session_state.parte = 1
if 'momento_azul' not in st.session_state: st.session_state.momento_azul = None

if 'log_eventos' not in st.session_state: st.session_state.log_eventos = []
if 'stats_iniciais' not in st.session_state: st.session_state.stats_iniciais = {}

if 'faltas_nos' not in st.session_state: st.session_state.faltas_nos = 0
if 'faltas_adv' not in st.session_state: st.session_state.faltas_adv = 0

equipa = st.session_state.equipa


# --- FUNÇÕES AUXILIARES ---
def formatar_tempo(segundos):
    return str(timedelta(seconds=int(segundos)))[2:]


def alternar_cronometro():
    if st.session_state.cronometro_correndo:
        st.session_state.tempo_acumulado += time.time() - st.session_state.cronometro_inicio
        st.session_state.cronometro_correndo = False
    else:
        st.session_state.cronometro_inicio = time.time()
        st.session_state.cronometro_correndo = True


def reiniciar_cronometro():
    st.session_state.cronometro_inicio = time.time()
    st.session_state.tempo_acumulado = 0
    st.session_state.cronometro_correndo = True


# ==========================================
# FASE 1: MENU PRINCIPAL
# ==========================================
def mostrar_menu():
    st.title("🏒 Parede FC Stats Tracker")
    st.markdown("Bem-vindo")
    st.divider()

    if st.button("⏱️ COMEÇAR NOVO JOGO", type="primary", use_container_width=True):
        st.session_state.fase = "config"
        st.rerun()


# ==========================================
# FASE 2: CONFIGURAÇÃO PRÉ-JOGO
# ==========================================
def mostrar_configuracao():
    st.title("📋 Configuração do Jogo")

    adv_input = st.text_input("Nome do Adversário:", placeholder="Ex: Sporting CP B")

    st.subheader("Escolhe o 5 Inicial")
    opcoes_jogadores = [f"{j.numero} - {j.nome}" for j in equipa.jogadores]

    selecionados = st.multiselect(
        "Seleciona exatamente 5 jogadores:",
        options=opcoes_jogadores,
        max_selections=5
    )

    st.divider()
    col1, col2 = st.columns([1, 4])

    if col1.button("⬅ Voltar"):
        st.session_state.fase = "menu"
        st.rerun()

    with col2:
        pode_comecar = len(selecionados) == 5 and adv_input.strip() != ""

        if st.button("🚀 INICIAR PARTIDA", type="primary", disabled=not pode_comecar, use_container_width=True):
            st.session_state.adversario = adv_input

            lista_final = []
            for s in selecionados:
                num = int(s.split(" - ")[0])
                obj = next(j for j in equipa.jogadores if j.numero == num)
                lista_final.append(obj)

            st.session_state.jogadores_em_campo = lista_final

            # guardar snapshot das estatísticas iniciais
            st.session_state.stats_iniciais = {}
            for j in equipa.jogadores:
                st.session_state.stats_iniciais[j.numero] = {
                    'golos': getattr(j, 'golos', 0),
                    'assistencias': getattr(j, 'assistencias', 0),
                    'azuis': getattr(j, 'azuis', 0),
                    'advertencias': getattr(j, 'advertencias', 0),
                    'plus_minus': getattr(j, 'plus_minus', 0),
                    "Faltas": getattr(j, 'faltas', 0),
                    "Perdas_posse": getattr(j, 'perdas_posse', 0) if j.posicao != "Guarda-Redes" else 0,
                    'defesas': getattr(j, 'defesas', 0) if j.posicao == "Guarda-Redes" else 0,
                    'golossofridos': getattr(j, 'golossofridos', 0) if j.posicao == "Guarda-Redes" else 0,
                    'bolasparadasdefendidas': getattr(j, 'bolasparadasdefendidas', 0) if j.posicao == "Guarda-Redes" else 0,
                    'bolasparadassofridas': getattr(j, 'bolasparadassofridas', 0) if j.posicao == "Guarda-Redes" else 0
                }

            # Reset variáveis
            st.session_state.golos_nos = 0
            st.session_state.golos_adv = 0
            st.session_state.tempo_acumulado = 0
            st.session_state.cronometro_correndo = False
            st.session_state.parte = 1
            st.session_state.momento_azul = None

            st.session_state.fase = "jogo"
            st.rerun()


# ==========================================
# FASE 3: INTERFACE DE JOGO (MATCH CENTER)
# ==========================================
def mostrar_jogo():
    # 1. BARRA SUPERIOR
    c1, c2 = st.columns([1, 6])
    if c1.button("⬅ Sair"):
            st.session_state.fase = "menu"
            st.rerun()

    # 3. PLACAR GRANDE
    st.markdown(f"""
        <div class="score-board">
            <h1 style='color: white; margin:0;'>PAREDE FC  <span style='color:#ff4b4b; font-size:60px'>{st.session_state.golos_nos}</span> - <span style='color:white; font-size:60px'>{st.session_state.golos_adv}</span>  {st.session_state.adversario}</h1>
            <h3 style='color: #fca311; margin:0; padding-top: 10px;'>Faltas: {st.session_state.faltas_nos} - {st.session_state.faltas_adv}</h3>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # 4. CONTROLOS DE TEMPO

    if st.button("💾 Guardar Jogo na base de dados", type="primary", use_container_width=True):
        novo_jogo = Jogo(
            st.session_state.adversario,
            st.session_state.golos_nos,
            st.session_state.golos_adv,
        )
        equipa.adicionar_jogo(novo_jogo)
        salvar_dados(equipa)
        st.success("Jogo Guardado!")

    # criar a tabela da época toda
    dados_epoca = []
    for j in equipa.jogadores:
        dados_epoca.append({
            "Nome": j.nome,
            "Numero": j.numero,
            "Posicao": j.posicao,
            "Golos": getattr(j, 'golos', 0),
            "Assistencias": getattr(j, 'assistencias', 0),
            "plus_minus": j.plus_minus,
            "Cartoes_Azuis": getattr(j, 'azuis', 0),
            "Advertencias": getattr(j, 'advertencias', 0),
            "Faltas": getattr(j, 'faltas', 0),
            "Perdas_posse": getattr(j, 'perdas_posse', 0) if j.posicao != "Guarda-Redes" else 0,
            "Defesas": getattr(j, 'defesas', 0) if j.posicao == "Guarda-Redes" else 0,
            "Golos_Sofridos": getattr(j, 'golossofridos', 0) if j.posicao == "Guarda-Redes" else 0,
            "Bolas_Paradas_Defendidas": getattr(j, "bolasparadasdefendidas", 0) if j.posicao == "Guarda-Redes" else 0,
            "Bolas_Paradas_Sofridas": getattr(j, "bolasparadassofridas", 0) if j.posicao == "Guarda-Redes" else 0,
        })

    # converter para Dataframe e depois para csv
    df_epoca = pd.DataFrame(dados_epoca)
    csv_epoca = df_epoca.to_csv(index=False, sep=";").encode("utf-8-sig")

    stats_jogo_atual = []

    if 'stats_iniciais' in st.session_state:
        for j in equipa.jogadores:
            inicial = st.session_state.stats_iniciais.get(j.numero, {})

            # valores atuais (fim de jogo)
            atual_golos = getattr(j, 'golos', 0)
            atual_assistencias = getattr(j, 'assistencias', 0)
            atual_azuis = getattr(j, 'azuis', 0)
            atual_advetencias = getattr(j, 'advetencias', 0)
            atual_pm = j.plus_minus
            atual_defesas = getattr(j, 'defesas', 0) if j.posicao == "Guarda-Redes" else 0
            atual_golossofridos = getattr(j, 'golossofridos', 0) if j.posicao == "Guarda-Redes" else 0
            atual_bolasparadasdefendidas = getattr(j, 'bolasparadasdefendidas', 0) if j.posicao == "Guarda-Redes" else 0
            atual_bolasparadassofridas = getattr(j, 'bolasparadassofridas', 0) if j.posicao == "Guarda-Redes" else 0

            # calculo da difernça (o que aconteceu no jogo atual)
            golos_hoje = atual_golos - inicial.get('golos', 0)
            assistencias_hoje = atual_assistencias - inicial.get('assistencias', 0)
            azuis_hoje = atual_azuis - inicial.get('azuis', 0)
            advertencias_hoje = atual_advetencias - inicial.get('advetencias', 0)
            pm_hoje = atual_pm - inicial.get('plus_minus', 0)
            defesas_hoje = atual_defesas - inicial.get('defesas', 0)
            golossofridos_hoje = atual_golossofridos - inicial.get('golossofridos', 0)
            bolasparadasdefendidas_hoje = atual_bolasparadasdefendidas - inicial.get('bolasparadasdefendidas', 0)
            bolasparadassofridas_hoje = atual_bolasparadassofridas - inicial.get('bolasparadassofridas', 0)

            if (golos_hoje + assistencias_hoje + azuis_hoje + advertencias_hoje + defesas_hoje + golossofridos_hoje + bolasparadasdefendidas_hoje + bolasparadassofridas_hoje != 0) or (pm_hoje != 0):
                stats_jogo_atual.append({
                    "numero": j.numero,
                    "nome": j.nome,
                    "golos": golos_hoje,
                    "assistencias": assistencias_hoje,
                    "plus_minus": pm_hoje,
                    "cartoes_azuis": azuis_hoje,
                    "defesas": defesas_hoje if j.posicao == "Guarda-Redes" else "-",
                    "golossofridos": golossofridos_hoje if j.posicao == "Guarda-Redes" else "-",
                    "bolasparadasdefendidas": bolasparadasdefendidas_hoje if j.posicao == "Guarda-Redes" else "-",
                    "bolasparadassofridas": bolasparadassofridas_hoje if j.posicao == "Guarda-Redes" else "-"
                })

        # 2. Converter os stats do jogo atual para CSV
        if len(stats_jogo_atual) > 0:
            df_jogo = pd.DataFrame(stats_jogo_atual)
        else:
            # se não aconteceu nada, cria uma tabela vazia com aviso
            df_jogo = pd.DataFrame([{"Aviso": "Sem dados registados neste jogo."}])

        # o sep=";" ajuda o Excel a separar logo as colunas automaticamente
        csv_jogo = df_jogo.to_csv(index=False, sep=";").encode('utf-8-sig')

        nome_ficheiro_jogo = f"Jogo_{st.session_state.adversario.replace(' ', '_')}.csv"

        # --- BOTÕES DE DESCARREGAR LADO A LADO ---
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📊 Descarregar Estatísticas da Época",
                data=csv_epoca,
                file_name="Estatisticas_Epoca_ParedeFC.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_geral"
            )
        with col_dl2:
            st.download_button(
                label=f"📄 Descarregar Jogo vs {st.session_state.adversario}",
                data=csv_jogo,
                file_name=nome_ficheiro_jogo,
                mime="text/csv",
                use_container_width=True,
                key="download_jogo"
            )

        st.write("---")

        # --- BOTÃO DE BACKUP (JSON) ---
        st.markdown("**Área do Analista (Backup)**")
        try:
            with open("dados_equipa.json", "r", encoding="utf-8") as f:
                db_json = f.read()
            st.download_button(
                label="⚙️ Descarregar Base de Dados Atualizada (JSON)",
                data=db_json,
                file_name="dados_equipa_atualizados.json",
                mime="application/json",
                use_container_width=True,
                key="download_json_backup"
            )
        except FileNotFoundError:
            st.warning("Guarda o jogo para gerar o backup.")

    st.divider()

    # 5. CARTÃO AZUL (SEM REGRA DE GOLO)
    if st.session_state.momento_azul:
        decorrido_azul = time.time() - st.session_state.momento_azul
        falta = 120 - int(decorrido_azul)
        if falta > 0:
            st.error(f"⛔ UNDERPLAY (AZUL): Faltam {falta}s!")
        else:
            st.success("✅ Tempo cumprido! Podes meter o jogador.")
            if st.button("Limpar Aviso Azul"):
                st.session_state.momento_azul = None
                st.rerun()

    # 6. CAMPO E JOGADORES
    col_campo, col_adversario = st.columns([3, 1])

    with col_campo:
        st.subheader("🏃‍♂️ Em Campo")

        for i, jogador in enumerate(st.session_state.jogadores_em_campo):
            # Layout das colunas para cada jogador
            cols = st.columns([3, 1, 1, 1, 1, 1, 1, 1, 1, 1])

            # COLUNA 0: Nome e Stats
            cols[0].markdown(f"**{jogador.numero}. {jogador.nome}** (PM: {jogador.plus_minus})")

            # COLUNA 1: Golo
            if cols[1].button("⚽", key=f"golo_{i}", help="Golo Marcado"):
                jogador.processar_evento("golo marcado", jogadores_em_campo=st.session_state.jogadores_em_campo)
                st.session_state.golos_nos += 1
                st.rerun()

            # COLUNA 2: Lógica Inteligente (Defesa para GR, Assist para Campo)
            if jogador.posicao == "Guarda-Redes":
                # Botão de Defesa (Luva)
                if cols[2].button("🧤", key=f"def_{i}", help="Registar Defesa"):
                    # Garante que o atributo existe
                    if not hasattr(jogador, 'defesas'): jogador.defesas = 0
                    jogador.defesas += 1
                    st.toast(f"Defesa do {jogador.nome}!")
                # botão bola parada defendida
                if cols[3].button("✋", key=f"bpd_{i}", help="Bola Parada Defendida"):
                    if not hasattr(jogador, 'bolasparadasdefendidas'): jogador.bolasparadasdefendidas = 0
                    jogador.bolasparadasdefendidas += 1
                    st.toast(f"BP defendida! ({jogador.nome}")
                # botão bola parada sofrida
                if cols[4].button("❌", key=f"bps_{i}", help="Bola Parada Sofrida"):
                    if not hasattr(jogador, 'bolasparadassofridas'): jogador.bolasparadassofridas = 0
                    jogador.bolasparadassofridas += 1
                    st.toast(f"BP sofrida! ({jogador.nome}")
            else:
                # Botão de Assistência (Sapatilha)
                if cols[2].button("👟", key=f"ass_{i}", help="Assistência"):
                    jogador.processar_evento("assistencia")
                    st.toast(f"Assistência: {jogador.nome}")

            # COLUNA 5: Azul
            if cols[5].button("🟦", key=f"azul_{i}", help="Cartão Azul"):
                if not hasattr(jogador, 'azuis'): jogador.azuis = 0
                jogador.azuis += 1

                tempo = formatar_tempo(st.session_state.tempo_acumulado + (time.time() - st.session_state.cronometro_inicio if st.session_state.cronometro_correndo else 0))

                st.session_state.momento_azul = time.time()
                st.session_state.jogadores_em_campo.pop(i)
                st.rerun()

            # COLUNA 6: advertência
            if cols[6].button("🟨", key=f"ama_{i}", help="Cartão Amarelo"):
                if not hasattr(jogador, 'advertencias'): jogador.advertencias = 0
                jogador.advertencias += 1
                st.toast(f"Amarelo para {jogador.nome}")

            # Coluna 7: falta cometida(Atualiza o Jogador E a Equipa)
            if cols[7].button("🛑", key=f"falta_{i}", help="Falta Cometida"):
                jogador.processar_evento("falta") # Soma 1 falta ao jogador no backend
                st.session_state.faltas_nos += 1  # Soma 1 falta à equipa no Placar!

                st.toast(f"Falta de {jogador.nome}! Total da Equipa: {st.session_state.faltas_nos}")
                st.rerun()

            # COLUNA 8: Perda de posse
            if jogador.posicao != "Guarda-Redes":
                if cols[8].button("📉", key=f"perda_{i}", help="Perda de Posse"):
                    jogador.processar_evento("perda de posse")
                    st.toast(f"Perda de posse: {jogador.nome}")

            # COLUNA 9: Substituição
            if cols[9].button("⬇", key=f"sai_{i}", help="Substituir"):
                st.session_state.jogadores_em_campo.pop(i)
                st.rerun()

        st.markdown("---")
        # Substituições
        with st.expander("🔄 Realizar Substituição", expanded=True):
            banco = [j for j in equipa.jogadores if j not in st.session_state.jogadores_em_campo]
            opcoes_banco = [f"{j.numero} - {j.nome}" for j in banco]

            jogador_entra_str = st.selectbox("Quem entra?", options=opcoes_banco, key="sub_box")

            if st.button("Entrar em Campo", type="secondary"):
                if len(st.session_state.jogadores_em_campo) < 5 and jogador_entra_str:
                    num = int(jogador_entra_str.split(" - ")[0])
                    obj = next(j for j in equipa.jogadores if j.numero == num)
                    st.session_state.jogadores_em_campo.append(obj)
                    st.rerun()
                elif len(st.session_state.jogadores_em_campo) >= 5:
                    st.error("Campo cheio!")

    # COLUNA DA DIREITA (Eventos Globais)
    with col_adversario:
        # Espaçamento para alinhar (Removemos o título "Adversário")
        st.write("")
        st.write("")

        if st.button("🥅 GOLO SOFRIDO", type="primary", use_container_width=True):
            st.session_state.golos_adv += 1
            for j in st.session_state.jogadores_em_campo:
                j.plus_minus -= 1
            st.toast("Golo sofrido! +/- atualizado.")
            st.rerun()

        st.write("---")

        if st.button(f"🛑 Falta [{st.session_state.adversario}]", use_container_width=True):
            st.session_state.faltas_adv += 1
            st.toast(f"Falta do adversário! Total: {st.session_state.faltas_adv}")
            st.rerun()

    st.write("---")

    st.divider()

    # 7. TABELA
    st.subheader("📊 Estatísticas em Tempo Real")
    dados_tabela = []
    for j in equipa.jogadores:
        dados = {
            "Nº": j.numero,
            "Nome": j.nome,
            "Golos": getattr(j, 'golos', 0),
            "Assist": getattr(j, 'assistencias', 0),
            "+/-": j.plus_minus,
            "Azuis": getattr(j, 'azuis', 0),
            "Advertencias": getattr(j, 'advertencias', 0),
            "Faltas": getattr(j, 'faltas', 0),
            "Perdas_Posse": getattr(j, 'perdas_posse', 0) if jogador.posicao != "Guarda-Redes" else 0
        }
        if j.posicao == "Guarda-Redes":
            dados["Defesas"] = getattr(j, 'defesas', 0)
            dados["Golos sofridos"] = getattr(j, 'golos_sofridos', 0)
            dados["BP Defendidas"] = getattr(j, 'bolasparadasdefendidas', 0)
            dados["BP Sofridas"] = getattr(j, 'bolasparadassofridas', 0)
        else:
            dados["Defesas"] = "-"
            dados["Golos sofridos"] = "-"
            dados["BP Defendidas"] = "-"
            dados["BP Sofridas"] = "-"

        dados_tabela.append(dados)

    df = pd.DataFrame(dados_tabela).set_index("Nº")
    st.dataframe(df, use_container_width=True)


# ==========================================
# CONTROLADOR DE PÁGINAS E UPDATE TIMER
# ==========================================
if st.session_state.fase == "menu":
    mostrar_menu()
elif st.session_state.fase == "config":
    mostrar_configuracao()
elif st.session_state.fase == "jogo":
    mostrar_jogo()

if st.session_state.cronometro_correndo:
    time.sleep(1)
    st.rerun()
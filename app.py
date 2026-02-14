import streamlit as st
import pandas as pd
import time
from datetime import timedelta

# --- IMPORTA AS TUAS CLASSES ---
try:
    from Projeto_StatsTracker import carregar_dados, salvar_dados, Jogo
except ImportError:
    st.error("Erro: O ficheiro 'Projeto_StatsTracker.py' não está na mesma pasta.")
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
    st.markdown("Bem-vindo, Mister.")
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
        if st.button("Confirmar Saída?"):
            st.session_state.fase = "menu"
            st.rerun()

    # 2. CÁLCULO DO TEMPO REAL
    tempo_atual = st.session_state.tempo_acumulado
    if st.session_state.cronometro_correndo:
        tempo_atual += time.time() - st.session_state.cronometro_inicio

    texto_tempo = formatar_tempo(tempo_atual)

    # 3. PLACAR GRANDE
    st.markdown(f"""
        <div class="score-board">
            <h1 style='color: white; margin:0;'>PAREDE FC  <span style='color:#ff4b4b; font-size:60px'>{st.session_state.golos_nos}</span> - <span style='color:white; font-size:60px'>{st.session_state.golos_adv}</span>  {st.session_state.adversario}</h1>
            <h2 style='color: #fca311; margin:0;'>{st.session_state.parte}ª PARTE | ⏱ {texto_tempo}</h2>
        </div>
    """, unsafe_allow_html=True)

    # 4. CONTROLOS DE TEMPO
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        btn_label = "⏸ PAUSAR" if st.session_state.cronometro_correndo else "▶ RETOMAR"
        if st.button(btn_label, use_container_width=True):
            alternar_cronometro()
            st.rerun()
    with col_t2:
        if st.button("🏁 Intervalo / 2ª Parte", use_container_width=True):
            st.session_state.parte = 2
            reiniciar_cronometro()
            st.session_state.cronometro_correndo = False
            st.rerun()
    with col_t3:
        if st.button("💾 Guardar Jogo", type="primary", use_container_width=True):
            novo_jogo = Jogo(
                st.session_state.adversario,
                st.session_state.golos_nos,
                st.session_state.golos_adv,
            )

            equipa.adicionar_jogo(novo_jogo)
            salvar_dados(equipa)
            st.success("Jogo Guardado!")
            time.sleep(2)
            st.session_state.fase = "menu"
            st.rerun()

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
            cols = st.columns([3, 1, 1, 1, 1])

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
            else:
                # Botão de Assistência (Sapatilha)
                if cols[2].button("👟", key=f"ass_{i}", help="Assistência"):
                    jogador.processar_evento("assistencia")
                    st.toast(f"Assistência: {jogador.nome}")

            # COLUNA 3: Azul
            if cols[3].button("🟦", key=f"azul_{i}", help="Cartão Azul"):
                st.session_state.momento_azul = time.time()
                st.session_state.jogadores_em_campo.pop(i)
                st.rerun()

            # COLUNA 4: Substituição
            if cols[4].button("⬇", key=f"sai_{i}", help="Substituir"):
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

        st.write("")
        if st.button("Falta Cometida", use_container_width=True):
            st.toast("Falta registada.")

        st.write("")
        # Botão para contar Bolas Paradas contra (ex: Livres/Penalties)
        if st.button("Bola Parada (Contra)", use_container_width=True):
            st.toast("Bola parada contra registada.")

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
            "Azuis": j.azuis
        }
        if j.posicao == "Guarda-Redes":
            dados["Defesas"] = getattr(j, 'defesas', 0)
        else:
            dados["Defesas"] = "-"
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
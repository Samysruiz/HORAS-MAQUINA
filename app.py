# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import urllib.parse
import requests
import json
from io import StringIO
from datetime import datetime, date, time

# ---------------- GITHUB ----------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO  = st.secrets["GITHUB_REPO"]
BRANCH       = "main"

def ler_csv_github(caminho, colunas):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{caminho}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        conteudo = base64.b64decode(r.json()["content"]).decode()
        return pd.read_csv(StringIO(conteudo))
    return pd.DataFrame(columns=colunas)

def salvar_csv_github(df, caminho):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{caminho}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    conteudo = base64.b64encode(df.to_csv(index=False).encode()).decode()
    r = requests.get(url + f"?ref={BRANCH}", headers=headers)
    sha = r.json().get("sha", "") if r.status_code == 200 else ""
    payload = {
        "message": f"update {caminho}",
        "content": conteudo,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    resp = requests.put(url, headers=headers, data=json.dumps(payload))
    if resp.status_code not in [200, 201]:
        st.error(f"Erro: {resp.status_code} - {resp.json().get('message', '')}")

# ---------------- LOGO ----------------  ✅ corrigido para arquivos grandes
def get_logo():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/LOGO.png?ref={BRANCH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            download_url = r.json().get("download_url")
            img = requests.get(download_url)
            return base64.b64encode(img.content).decode()
    except:
        pass
    return ""

LOGO_B64 = get_logo()

def show_logo(width=220, center=False):
    if not LOGO_B64:
        return
    align = "center" if center else "left"
    st.markdown(
        f'<div style="text-align:{align};margin-bottom:8px">'
        f'<img src="data:image/png;base64,{LOGO_B64}" width="{width}px"></div>',
        unsafe_allow_html=True
    )

# ---------------- ESTILO ----------------
st.markdown("""
<style>
.stButton>button{
    background-color:#E41E26;
    color:white;
    border-radius:8px;
    height:45px;
    font-weight:bold;
}
section[data-testid="stSidebar"] .stButton>button{
    height:35px;
}
.salvo{
    font-size:2.5rem;
    font-weight:bold;
    color:#1a7a1a;
    text-align:center;
    padding:20px;
    border:3px solid #1a7a1a;
    border-radius:12px;
    margin:10px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
USUARIO = "SANDRO"
SENHA = "123"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        show_logo(280, True)
        st.markdown("<h2 style='text-align:center;color:#E41E26;'>Sandro Bobcat</h2>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            if usuario.upper() == USUARIO and senha == SENHA:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuario ou senha incorretos")
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    show_logo(160, True)
    st.markdown("---")
    menu = st.selectbox("", [
        "Registrar Horas",
        "Empregadores",
        "Cobrar Horas",
        "Metricas",
        "Arquivo"
    ])
    st.markdown("---")
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

# ---------------- ARQUIVOS ----------------
emp      = ler_csv_github("empregadores.csv", ["empresa","whats","valor_hora"])
horas    = ler_csv_github("horas.csv", ["empresa","data","horas","valor"])
cobradas = ler_csv_github("cobradas.csv", ["empresa","data","horas","valor"])

# ---------------- EMOJIS ----------------
TRUCK    = chr(0x1F69C)
BUILDING = chr(0x1F3E2)
CALENDAR = chr(0x1F4C5)
TIMER    = chr(0x23F1)
MONEY    = chr(0x1F4B0)
CHECK    = chr(0x2705)
HANDS    = chr(0x1F91D)
LINE     = "\u2501" * 22

# ---------------- EMPREGADORES ----------------
if menu == "Empregadores":
    st.title("Empregadores")

    with st.container(border=True):
        st.subheader("Cadastrar cliente")
        empresa = st.text_input("Empresa")
        whats = st.text_input("WhatsApp")
        valor = st.number_input("Valor hora (R$)", min_value=0.0, value=120.0)

        if st.button("Salvar", use_container_width=True):
            if empresa in emp["empresa"].values:
                st.warning("Cliente ja cadastrado!")
            else:
                novo = pd.DataFrame([{"empresa":empresa,"whats":whats,"valor_hora":valor}])
                emp = pd.concat([emp,novo], ignore_index=True)
                salvar_csv_github(emp, "empregadores.csv")
                st.toast("Cliente cadastrado!", icon="✅")
                st.rerun()

    st.markdown("---")
    st.subheader("Clientes cadastrados")

    if emp.empty:
        st.info("Nenhum cliente cadastrado")
    else:
        for i, row in emp.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([4,1,1])
                with col1:
                    st.write(f"**{row['empresa']}** | {row['whats']} | R$ {row['valor_hora']}/h")
                with col2:
                    if st.button("editar", key=f"edit_{i}"):
                        st.session_state[f"editar_{i}"] = True
                with col3:
                    if st.button("apagar", key=f"del_{i}"):
                        cliente = row["empresa"]
                        emp = emp.drop(i).reset_index(drop=True)
                        salvar_csv_github(emp, "empregadores.csv")
                        horas = horas[horas["empresa"] != cliente].reset_index(drop=True)
                        salvar_csv_github(horas, "horas.csv")
                        cobradas = cobradas[cobradas["empresa"] != cliente].reset_index(drop=True)
                        salvar_csv_github(cobradas, "cobradas.csv")
                        st.toast(f"Cliente {cliente} removido!", icon="🗑️")
                        st.rerun()

            if st.session_state.get(f"editar_{i}"):
                with st.form(key=f"form_{i}"):
                    nova_empresa = st.text_input("Empresa", value=row["empresa"])
                    novo_whats = st.text_input("WhatsApp", value=row["whats"])
                    novo_valor = st.number_input("Valor hora", value=float(row["valor_hora"]))
                    if st.form_submit_button("Salvar edicao"):
                        emp.at[i,"empresa"] = nova_empresa
                        emp.at[i,"whats"] = novo_whats
                        emp.at[i,"valor_hora"] = novo_valor
                        salvar_csv_github(emp, "empregadores.csv")
                        del st.session_state[f"editar_{i}"]
                        st.toast("Cliente atualizado!", icon="✅")
                        st.rerun()

# ---------------- REGISTRAR HORAS ----------------
if menu == "Registrar Horas":
    st.title("Registrar Horas")

    if emp.empty:
        st.warning("Cadastre um cliente primeiro")
    else:
        with st.container(border=True):
            empresa = st.selectbox("Empresa", emp["empresa"])
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.radio(
                    "Tipo registro",
                    ["Inicio/Fim", "Meio dia (4h)", "Dia todo (8h)"],
                    horizontal=True
                )
            with col2:
                data = date.today()
                st.info(f"Data: **{data.strftime('%d/%m/%Y')}** (somente hoje)")

        horas_trab = 0

        with st.container(border=True):
            if tipo == "Inicio/Fim":
                col1, col2 = st.columns(2)
                with col1:
                    inicio = st.time_input("Inicio", value=time(7, 0))
                with col2:
                    fim = st.time_input("Fim", value=time(17, 0))
                if fim <= inicio:
                    st.error("Hora fim deve ser maior que hora inicio")
                else:
                    diff = datetime.combine(data, fim) - datetime.combine(data, inicio)
                    horas_trab = diff.seconds / 3600

            elif tipo == "Meio dia (4h)":
                horas_trab = 4
                extra = st.time_input("Horas extras", value=time(0, 0))
                horas_trab += extra.hour + extra.minute / 60

            elif tipo == "Dia todo (8h)":
                horas_trab = 8
                extra = st.time_input("Horas extras", value=time(0, 0))
                horas_trab += extra.hour + extra.minute / 60

            horas_exibir = int(horas_trab)
            minutos_exibir = int((horas_trab - horas_exibir) * 60)
            st.success(f"Total: {horas_exibir}h {minutos_exibir:02d}min")

            data_str = data.strftime("%d/%m/%Y")
            ja_registrado = (
                not horas.empty and
                ((horas["empresa"] == empresa) & (horas["data"] == data_str)).any()
            )

            if ja_registrado:
                st.error(f"Voce ja trabalhou para {empresa} hoje! Edite no Arquivo se precisar corrigir.")
            else:
                if st.button("Salvar horas", use_container_width=True):
                    st.session_state["confirmar"] = True

            if st.session_state.get("confirmar") and not ja_registrado:
                st.warning(
                    f"Confirma salvar **{horas_exibir}h {minutos_exibir:02d}min** "
                    f"para **{empresa}** no dia **{data_str}**?"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sim, salvar", use_container_width=True):
                        valor_hora = emp.loc[emp["empresa"] == empresa, "valor_hora"].values[0]
                        novo = pd.DataFrame([{
                            "empresa": empresa,
                            "data": data_str,
                            "horas": horas_trab,
                            "valor": horas_trab * valor_hora
                        }])
                        horas = pd.concat([horas, novo], ignore_index=True)
                        salvar_csv_github(horas, "horas.csv")
                        st.session_state["confirmar"] = False
                        st.session_state["salvo"] = True
                        st.rerun()
                with col2:
                    if st.button("Cancelar", use_container_width=True):
                        st.session_state["confirmar"] = False
                        st.rerun()

        if st.session_state.get("salvo"):
            st.markdown(
                '<div class="salvo">HORAS SALVAS COM SUCESSO!</div>',
                unsafe_allow_html=True
            )
            st.balloons()
            st.session_state["salvo"] = False

# ---------------- COBRAR HORAS ----------------
if menu == "Cobrar Horas":
    st.title("Cobrar Horas")

    if horas.empty:
        st.info("Nenhuma hora registrada")
    else:
        empresa = st.selectbox("Empresa", horas["empresa"].unique())
        dados = horas[horas["empresa"] == empresa].copy()
        dados_reset = dados.reset_index()

        with st.container(border=True):
            selecionados = st.dataframe(
                dados_reset[["data","horas","valor"]],
                use_container_width=True,
                on_select="rerun",
                selection_mode="multi-row"
            )

            if selecionados.selection.rows:
                if st.button("Apagar selecionados", use_container_width=True):
                    indices = dados_reset.iloc[selecionados.selection.rows]["index"].tolist()
                    horas = horas.drop(indices).reset_index(drop=True)
                    salvar_csv_github(horas, "horas.csv")
                    st.toast("Registros apagados!", icon="🗑️")
                    st.rerun()

            total_h = dados["horas"].sum()
            total_v = dados["valor"].sum()
            total_h_int = int(total_h)
            total_min_int = int((total_h - total_h_int) * 60)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total horas", f"{total_h_int}h {total_min_int:02d}min")
            with col2:
                st.metric("Saldo", f"R$ {total_v:.2f}")

        if st.button("Somar e mandar", use_container_width=True):
            telefone = emp.loc[emp["empresa"] == empresa, "whats"].values[0]
            datas = pd.to_datetime(dados["data"], format="%d/%m/%Y")
            data_ini = datas.min().strftime("%d/%m/%Y")
            data_fim = datas.max().strftime("%d/%m/%Y")

            mensagem = (
                "*SANDRO BOBCAT*\n"
                "--------------------\n"
                f"Cliente: *{empresa}*\n"
                f"Periodo: *{data_ini} a {data_fim}*\n"
                "--------------------\n"
                f"Horas: *{total_h_int}h {total_min_int:02d}min*\n"
                f"Valor: *R$ {total_v:.2f}*\n"
                "--------------------\n"
                "Obrigado pela confianca!"
            )

            cobradas = pd.concat([cobradas, dados], ignore_index=True)
            salvar_csv_github(cobradas, "cobradas.csv")
            horas = horas.drop(dados.index)
            salvar_csv_github(horas, "horas.csv")

            link = f"https://wa.me/{telefone}?text={urllib.parse.quote(mensagem)}"
            st.link_button("Enviar WhatsApp", link, use_container_width=True)

# ---------------- METRICAS ----------------
if menu == "Metricas":
    st.title("Metricas")

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Horas totais", f"{int(cobradas['horas'].sum())}h")
        with col2:
            st.metric("Saldo total", f"R$ {cobradas['valor'].sum():.2f}")
        with col3:
            st.metric("Clientes", emp.shape[0])

    if not cobradas.empty:
        graf = cobradas.groupby("empresa")["valor"].sum().reset_index()
        fig = px.bar(graf, x="empresa", y="valor", title="Faturamento por cliente")
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ARQUIVO ----------------
if menu == "Arquivo":
    st.title("Arquivo")

    st.subheader("Horas pendentes")
    if horas.empty:
        st.info("Nenhuma hora pendente")
    else:
        for i, row in horas.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([4,1,1])
                with col1:
                    h_int = int(row["horas"])
                    m_int = int((row["horas"] - h_int) * 60)
                    st.write(f"**{row['empresa']}** | {row['data']} | {h_int}h {m_int:02d}min | R$ {row['valor']:.2f}")
                with col2:
                    if st.button("editar", key=f"edit_h_{i}"):
                        st.session_state[f"editar_h_{i}"] = True
                with col3:
                    if st.button("apagar", key=f"del_h_{i}"):
                        horas = horas.drop(i).reset_index(drop=True)
                        salvar_csv_github(horas, "horas.csv")
                        st.toast("Registro apagado!", icon="🗑️")
                        st.rerun()

            if st.session_state.get(f"editar_h_{i}"):
                with st.form(key=f"form_h_{i}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_inicio = st.time_input("Inicio", value=time(7, 0))
                    with col2:
                        novo_fim = st.time_input("Fim", value=time(17, 0))
                    if st.form_submit_button("Salvar edicao"):
                        if novo_fim <= novo_inicio:
                            st.error("Hora fim deve ser maior que inicio")
                        else:
                            data_row = datetime.strptime(row["data"], "%d/%m/%Y").date()
                            diff = datetime.combine(data_row, novo_fim) - datetime.combine(data_row, novo_inicio)
                            novas_horas = diff.seconds / 3600
                            valor_hora = emp.loc[emp["empresa"] == row["empresa"], "valor_hora"].values[0]
                            horas.at[i, "horas"] = novas_horas
                            horas.at[i, "valor"] = novas_horas * valor_hora
                            salvar_csv_github(horas, "horas.csv")
                            del st.session_state[f"editar_h_{i}"]
                            st.toast("Horas atualizadas!", icon="✅")
                            st.rerun()

    st.markdown("---")
    st.subheader("Historico cobrado")
    if cobradas.empty:
        st.info("Nenhum historico")
    else:
        st.dataframe(cobradas, use_container_width=True)

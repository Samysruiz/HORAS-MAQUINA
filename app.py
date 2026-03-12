import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import urllib.parse

from datetime import datetime, date, time

# ---------------- LOGO ----------------
with open("LOGO.png", "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode()

def show_logo(width=220, center=False):
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

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):

            if usuario.upper() == USUARIO and senha == SENHA:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

    st.stop()

# ---------------- APP ----------------
show_logo()
st.title("Sandro Bobcat")

if st.button("🚪 Sair"):
    st.session_state.logado = False
    st.rerun()

# ---------------- ARQUIVOS ----------------
def criar(nome, colunas):
    if not os.path.exists(nome):
        pd.DataFrame(columns=colunas).to_csv(nome, index=False)

criar("empregadores.csv", ["empresa","whats","valor_hora"])
criar("horas.csv", ["empresa","data","horas","valor"])
criar("cobradas.csv", ["empresa","data","horas","valor"])

emp = pd.read_csv("empregadores.csv")
horas = pd.read_csv("horas.csv")
cobradas = pd.read_csv("cobradas.csv")

menu = st.selectbox("", [
"Registrar Horas",
"Empregadores",
"Cobrar Horas",
"Métricas",
"Arquivo"
])

# ---------------- EMPREGADORES ----------------
if menu == "Empregadores":

    st.subheader("Cadastrar cliente")

    empresa = st.text_input("Empresa")
    whats = st.text_input("WhatsApp")
    valor = st.number_input("Valor hora (R$)", min_value=0.0, value=120.0)

    if st.button("Salvar"):

        if empresa in emp["empresa"].values:
            st.warning("⚠️ Cliente já cadastrado!")
        else:
            novo = pd.DataFrame([{
                "empresa":empresa,
                "whats":whats,
                "valor_hora":valor
            }])

            emp = pd.concat([emp,novo], ignore_index=True)
            emp.to_csv("empregadores.csv", index=False)

            st.success("Cliente cadastrado!")
            st.rerun()

    st.markdown("---")
    st.subheader("Clientes cadastrados")

    if emp.empty:
        st.info("Nenhum cliente cadastrado")

    else:
        for i, row in emp.iterrows():

            col1, col2, col3 = st.columns([4,1,1])

            with col1:
                st.write(f"**{row['empresa']}** | 📞 {row['whats']} | R$ {row['valor_hora']}/h")

            with col2:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state[f"editar_{i}"] = True

            with col3:
                if st.button("🗑️", key=f"del_{i}"):

                    emp = emp.drop(i).reset_index(drop=True)
                    emp.to_csv("empregadores.csv", index=False)

                    st.success("Cliente removido")
                    st.rerun()

            if st.session_state.get(f"editar_{i}"):

                with st.form(key=f"form_{i}"):

                    nova_empresa = st.text_input("Empresa", value=row["empresa"])
                    novo_whats = st.text_input("WhatsApp", value=row["whats"])
                    novo_valor = st.number_input("Valor hora", value=float(row["valor_hora"]))

                    if st.form_submit_button("Salvar edição"):

                        emp.at[i,"empresa"] = nova_empresa
                        emp.at[i,"whats"] = novo_whats
                        emp.at[i,"valor_hora"] = novo_valor

                        emp.to_csv("empregadores.csv", index=False)

                        del st.session_state[f"editar_{i}"]

                        st.success("Cliente atualizado!")
                        st.rerun()

# ---------------- REGISTRAR HORAS ----------------
if menu == "Registrar Horas":

    if emp.empty:
        st.warning("Cadastre um cliente primeiro")

    else:

        empresa = st.selectbox("Empresa", emp["empresa"])

        tipo = st.radio("Tipo registro",
elif tipo == "Meio dia (4h)":

    horas_trab = 4

    extra = st.time_input("Horas extras", value=time(0,0))

    horas_trab += extra.hour + extra.minute/60


elif tipo == "Dia todo (8h)":

    horas_trab = 8

    extra = st.time_input("Horas extras", value=time(0,0))

    horas_trab += extra.hour + extra.minute/60

        data = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        horas_trab = 0

        if tipo == "Inicio/Fim":

            col1, col2 = st.columns(2)

            with col1:
                h_ini = st.number_input("Hora início",0,23,7)
                m_ini = st.number_input("Minuto início",0,59,0)

            with col2:
                h_fim = st.number_input("Hora fim",0,23,17)
                m_fim = st.number_input("Minuto fim",0,59,0)

            inicio = time(h_ini,m_ini)
            fim = time(h_fim,m_fim)

            if fim <= inicio:
                st.error("Hora fim deve ser maior")

            else:
                diff = datetime.combine(data,fim) - datetime.combine(data,inicio)
                horas_trab = diff.seconds/3600

        elif tipo == "Meio dia (4h)":
            horas_trab = 4

        elif tipo == "Dia todo (8h)":
            horas_trab = 8

        st.success(f"Total: {horas_trab:.2f} horas")

        if st.button("Salvar horas"):

            valor_hora = emp.loc[emp["empresa"]==empresa,"valor_hora"].values[0]

            novo = pd.DataFrame([{
                "empresa":empresa,
                "data":data.strftime("%d/%m/%Y"),
                "horas":horas_trab,
                "valor":horas_trab * valor_hora
            }])

            horas = pd.concat([horas,novo], ignore_index=True)
            horas.to_csv("horas.csv", index=False)

            st.success("Horas registradas!")

# ---------------- COBRAR HORAS ----------------
if menu == "Cobrar Horas":

    if horas.empty:
        st.info("Nenhuma hora registrada")

    else:

        empresa = st.selectbox("Empresa", horas["empresa"].unique())

        dados = horas[horas["empresa"]==empresa]

        st.dataframe(dados)

        total_h = dados["horas"].sum()
        total_v = dados["valor"].sum()

        st.metric("Total horas", total_h)
        st.metric("Saldo", f"R$ {total_v:.2f}")

        if st.button("Somar e mandar"):

            telefone = emp.loc[emp["empresa"]==empresa,"whats"].values[0]

            mensagem = f"""
🚜 *SANDRO BOBCAT*
━━━━━━━━━━━━━━━━━━
🏢 *{empresa}*
━━━━━━━━━━━━━━━━━━
⏱ Total horas: *{total_h}h*
💰 Saldo: *R$ {total_v:.2f}*
━━━━━━━━━━━━━━━━━━
🙏 Obrigado pelo serviço!
"""

            cobradas = pd.concat([cobradas,dados], ignore_index=True)
            cobradas.to_csv("cobradas.csv", index=False)

            horas = horas.drop(dados.index)
            horas.to_csv("horas.csv", index=False)

            link = f"https://wa.me/{telefone}?text={urllib.parse.quote(mensagem)}"

            st.link_button("Enviar WhatsApp", link)

# ---------------- MÉTRICAS ----------------
if menu == "Métricas":

    st.metric("Horas totais", cobradas["horas"].sum())
    st.metric("Saldo total", f"R$ {cobradas['valor'].sum():.2f}")
    st.metric("Clientes", emp.shape[0])

    if not cobradas.empty:

        graf = cobradas.groupby("empresa")["valor"].sum().reset_index()

        fig = px.bar(
            graf,
            x="empresa",
            y="valor",
            title="Faturamento por cliente"
        )

        st.plotly_chart(fig)

# ---------------- HISTÓRICO ----------------
if menu == "Arquivo":

    st.subheader("Histórico de horas cobradas")

    st.dataframe(cobradas)

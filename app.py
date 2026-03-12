
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

st.set_page_config(page_title="Sandro Bobcat", layout="centered")

st.image("logo.png", width=220)
st.title("Sandro Bobcat")

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

def criar(nome,colunas):
    if not os.path.exists(nome):
        pd.DataFrame(columns=colunas).to_csv(nome,index=False)

criar("empregadores.csv",["empresa","whats","valor_hora"])
criar("horas.csv",["empresa","data","horas","valor"])
criar("cobradas.csv",["empresa","data","horas","valor"])

emp = pd.read_csv("empregadores.csv")
horas = pd.read_csv("horas.csv")
cobradas = pd.read_csv("cobradas.csv")

menu = st.selectbox("",[
"Registrar Horas",
"Empregadores",
"Cobrar Horas",
"Métricas",
"Arquivo"
])

if menu=="Empregadores":

    st.subheader("Cadastrar empregador")

    empresa = st.text_input("Empresa")
    whats = st.text_input("WhatsApp")
    valor = st.number_input("Valor hora",120)

    if st.button("Salvar"):

        novo = pd.DataFrame([{
        "empresa":empresa,
        "whats":whats,
        "valor_hora":valor
        }])

        emp = pd.concat([emp,novo])
        emp.to_csv("empregadores.csv",index=False)

        st.success("Empregador salvo")

    st.dataframe(emp)

if menu=="Registrar Horas":

    if emp.empty:
        st.warning("Cadastre um empregador primeiro.")
    else:
        empresa = st.selectbox("Empresa",emp["empresa"])

        tipo = st.radio("Tipo registro",[
        "Inicio/Fim",
        "Meio dia (4h)",
        "Dia todo (8h)",
        "+ Horas manual"
        ])

        data = st.date_input("Data")

        horas_trab = 0

        if tipo=="Inicio/Fim":

            inicio = st.time_input("Hora inicio")
            fim = st.time_input("Hora fim")

            inicio_dt = datetime.combine(data,inicio)
            fim_dt = datetime.combine(data,fim)

            horas_trab = (fim_dt-inicio_dt).seconds/3600

        elif tipo=="Meio dia (4h)":
            horas_trab = 4

        elif tipo=="Dia todo (8h)":
            horas_trab = 8

        elif tipo=="+ Horas manual":
            horas_trab = st.number_input("Horas",0.0)

        if st.button("Salvar horas"):

            valor_hora = emp.loc[
            emp["empresa"]==empresa,"valor_hora"
            ].values[0]

            valor = horas_trab * valor_hora

            novo = pd.DataFrame([{
            "empresa":empresa,
            "data":data,
            "horas":horas_trab,
            "valor":valor
            }])

            horas = pd.concat([horas,novo])
            horas.to_csv("horas.csv",index=False)

            st.success("Horas registradas")

if menu=="Cobrar Horas":

    if horas.empty:
        st.info("Nenhuma hora registrada.")
    else:
        empresa = st.selectbox("Empresa",horas["empresa"].unique())

        dados = horas[horas["empresa"]==empresa]

        st.dataframe(dados)

        total_h = dados["horas"].sum()
        total_v = dados["valor"].sum()

        st.metric("Horas",total_h)
        st.metric("Saldo",f"R$ {total_v}")

        if st.button("Somar e mandar"):

            telefone = emp.loc[
            emp["empresa"]==empresa,"whats"
            ].values[0]

            mensagem=f"""
Relatório de serviço

Empresa: {empresa}

Total horas: {total_h}
Saldo: R${total_v}

Obrigado por usar nossos serviços

Sandro Bobcat
"""

            link=f"https://wa.me/{telefone}?text={mensagem}"

            cobradas = pd.concat([cobradas,dados])
            cobradas.to_csv("cobradas.csv",index=False)

            horas.drop(dados.index,inplace=True)
            horas.to_csv("horas.csv",index=False)

            st.link_button("Enviar WhatsApp",link)

if menu=="Métricas":

    st.metric("Horas mês",cobradas["horas"].sum())
    st.metric("Saldo total",cobradas["valor"].sum())
    st.metric("Empregadores",emp.shape[0])

    if not cobradas.empty:
        graf = cobradas.groupby("empresa")["valor"].sum()
        fig = px.bar(graf)
        st.plotly_chart(fig)

if menu=="Arquivo":

    st.subheader("Horas trabalhadas")

    st.dataframe(cobradas)

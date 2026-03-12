import streamlit as st
import base64

with open("logo.png", "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode()

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

def show_logo(width=220, center=False):
    align = "center" if center else "left"
    st.markdown(
        f'<div style="text-align:{align};margin-bottom:8px"><img src="data:image/png;base64,{LOGO_B64}" width="{width}px"></div>',
        unsafe_allow_html=True
    
    )

USUARIO = "SANDRO"
SENHA   = "123"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        show_logo(width=280, center=True)
        st.markdown("<h2 style='text-align:center;color:#E41E26;'>Sandro Bobcat</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha   = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        if st.button("Entrar", use_container_width=True):
            if usuario.upper() == USUARIO and senha == SENHA:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    st.stop()

# ── APP ──
show_logo(220)
st.title("Sandro Bobcat")
if st.button("🚪 Sair"):
    st.session_state.logado = False
    st.rerun()

def criar(nome, colunas):
    if not os.path.exists(nome):
        pd.DataFrame(columns=colunas).to_csv(nome, index=False)

criar("empregadores.csv", ["empresa","whats","valor_hora"])
criar("horas.csv",        ["empresa","data","horas","valor"])
criar("cobradas.csv",     ["empresa","data","horas","valor"])

emp      = pd.read_csv("empregadores.csv")
horas    = pd.read_csv("horas.csv")
cobradas = pd.read_csv("cobradas.csv")

menu = st.selectbox("", ["Registrar Horas","Empregadores","Cobrar Horas","Métricas","Arquivo"])

# ── EMPREGADORES ──
if menu == "Empregadores":
    st.subheader("Cadastrar empregador")
    empresa = st.text_input("Empresa")
    whats   = st.text_input("WhatsApp")
    valor   = st.number_input("Valor hora (R$)", min_value=0.0, value=120.0, step=0.5)
    if st.button("💾 Salvar"):                                          # ✅ CORRIGIDO: removido st.success duplicado e indentação corrigida
        novo = pd.DataFrame([{"empresa": empresa, "whats": whats, "valor_hora": valor}])
        emp  = pd.concat([emp, novo], ignore_index=True)
        emp.to_csv("empregadores.csv", index=False)
        st.success("Empregador salvo!")
        st.rerun()

    st.markdown("---")
    st.subheader("Empregadores cadastrados")
    if emp.empty:
        st.info("Nenhum empregador cadastrado.")
    else:
        for i, row in emp.iterrows():
            col1, col2, col3 = st.columns([4,1,1])
            with col1:
                st.write(f"**{row['empresa']}** | 📞 {row['whats']} | R$ {row['valor_hora']}/h")
            with col2:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state[f"editing_{i}"] = True
            with col3:
                if st.button("🗑️", key=f"del_{i}"):
                    emp = emp.drop(index=i).reset_index(drop=True)
                    emp.to_csv("empregadores.csv", index=False)
                    st.success("Excluído!")
                    st.rerun()
            if st.session_state.get(f"editing_{i}"):
                with st.form(key=f"form_edit_{i}"):
                    ne = st.text_input("Empresa",    value=row["empresa"])
                    nw = st.text_input("WhatsApp",   value=row["whats"])
                    nv = st.number_input("Valor hora", value=float(row["valor_hora"]), step=0.5)
                    if st.form_submit_button("Salvar edição"):
                        emp.at[i, "empresa"]    = ne
                        emp.at[i, "whats"]      = nw
                        emp.at[i, "valor_hora"] = nv
                        emp.to_csv("empregadores.csv", index=False)
                        del st.session_state[f"editing_{i}"]
                        st.rerun()

# ── REGISTRAR HORAS ──
if menu == "Registrar Horas":
    if emp.empty:
        st.warning("Cadastre um empregador primeiro.")
    else:
        empresa = st.selectbox("Empresa", emp["empresa"])

        tipo = st.radio("Tipo de registro", [
            "Inicio/Fim",
            "Meio dia (4h)",
            "Dia todo (8h)"
        ])

        data = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")

        horas_trab = 0.0

        if tipo == "Inicio/Fim":
            col1, col2 = st.columns(2)
            with col1:
                h_ini = st.number_input("Hora início", min_value=0, max_value=23, value=7, step=1)
                m_ini = st.number_input("Minuto início", min_value=0, max_value=59, value=0, step=5)
            with col2:
                h_fim = st.number_input("Hora fim", min_value=0, max_value=23, value=17, step=1)
                m_fim = st.number_input("Minuto fim", min_value=0, max_value=59, value=0, step=5)

            inicio = time(h_ini, m_ini)
            fim    = time(h_fim, m_fim)

            if fim <= inicio:
                st.error("⚠️ Hora fim deve ser maior que hora início!")
                horas_trab = 0.0
            else:
                diff = datetime.combine(data, fim) - datetime.combine(data, inicio)
                horas_trab = diff.seconds / 3600
                st.info(f"⏱️ Total: **{horas_trab:.2f} horas**  ({h_ini:02d}:{m_ini:02d} → {h_fim:02d}:{m_fim:02d})")

        elif tipo == "Meio dia (4h)":
            horas_trab = 4.0
            st.info("⏱️ Total: **4.00 horas**")

        elif tipo == "Dia todo (8h)":
            horas_trab = 8.0
            st.info("⏱️ Total: **8.00 horas**")

        st.success(f"✅ Total final: **{horas_trab:.2f} horas**")

        if st.button("💾 Salvar horas"):
            valor_hora = emp.loc[emp["empresa"] == empresa, "valor_hora"].values[0]
            novo  = pd.DataFrame([{
                "empresa": empresa,
                "data":    data.strftime("%d/%m/%Y"),
                "horas":   round(horas_trab, 2),
                "valor":   round(horas_trab * valor_hora, 2)
            }])
            horas = pd.concat([horas, novo], ignore_index=True)
            horas.to_csv("horas.csv", index=False)
            st.success("✅ Horas registradas!")

# ── COBRAR HORAS ──
if menu == "Cobrar Horas":
    if horas.empty:
        st.info("Nenhuma hora registrada.")
    else:
        empresa = st.selectbox("Empresa", horas["empresa"].unique())
        dados   = horas[horas["empresa"] == empresa]
        st.dataframe(dados, use_container_width=True)
        total_h = round(dados["horas"].sum(), 2)
        total_v = round(dados["valor"].sum(), 2)
        st.metric("Total Horas", total_h)
        st.metric("Saldo", f"R$ {total_v:,.2f}")
        enviar_tabela = st.checkbox("📋 Incluir tabela de horas na mensagem")

        if st.button("📤 Somar e mandar"):
            import urllib.parse
            telefone = emp.loc[emp["empresa"] == empresa, "whats"].values[0]

            tabela_str = ""
            if enviar_tabela:
                linhas = ["\n📅 *Detalhamento:*"]
                for _, r in dados.iterrows():
                    linhas.append(f"  • {r['data']} | {r['horas']}h | R$ {float(r['valor']):.2f}")
                tabela_str = "\n".join(linhas)

            mensagem = (
                "🚜 *SANDRO BOBCAT*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🏢 *{empresa}*\n"
                f"{tabela_str}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱ Total de horas: *{total_h}h*\n"
                f"💰 Saldo: *R$ {total_v:.2f}*\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🙏 Obrigado pelo serviço!"
            )

            cobradas = pd.concat([cobradas, dados], ignore_index=True)
            cobradas.to_csv("cobradas.csv", index=False)
            horas = horas.drop(dados.index).reset_index(drop=True)
            horas.to_csv("horas.csv", index=False)
            st.link_button("📱 Enviar WhatsApp", f"https://wa.me/{telefone}?text={urllib.parse.quote(mensagem)}")

# ── MÉTRICAS ──
if menu == "Métricas":
    st.metric("Horas (histórico)",  cobradas["horas"].sum())
    st.metric("Saldo total",        f"R$ {cobradas['valor'].sum():,.2f}")
    st.metric("Empregadores",       emp.shape[0])
    if not cobradas.empty:
        graf = cobradas.groupby("empresa")["valor"].sum().reset_index()
        fig  = px.bar(graf, x="empresa", y="valor", title="Faturamento por empresa", color="empresa")
        st.plotly_chart(fig, use_container_width=True)

# ── ARQUIVO ──
if menu == "Arquivo":
    st.subheader("Histórico de horas cobradas")
    st.dataframe(cobradas, use_container_width=True)

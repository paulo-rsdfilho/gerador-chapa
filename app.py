import streamlit as st
import ezdxf
from io import BytesIO, TextIOWrapper
import requests
import time

# =========================
# CONFIG DA PÁGINA (remove menu)
# =========================
st.set_page_config(
    page_title="Gerador de Chapa",
    layout="centered",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Esconde menu e footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# =========================
# CONFIG BLOQUEIO REMOTO
# =========================
URL_STATUS = "https://raw.githubusercontent.com/paulo-rsdfilho/controle-app/refs/heads/main/status.json"

def verificar_acesso():
    try:
        r = requests.get(URL_STATUS, timeout=3)
        data = r.json()

        if not data.get("ativo", False):
            st.error(data.get("mensagem", "Sistema desativado"))
            st.stop()

    except:
        st.error("Erro ao verificar acesso")
        st.stop()

# Executa verificação
verificar_acesso()

# =========================
# CONFIG CHAPA
# =========================
W = 88
R = 10
furo_d = 10
offset_x = 100
offset_y = 10

def gerar_dxf_perfeito(L):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    msp.add_lwpolyline([
        (0, R, 0.41421356),
        (R, 0, 0),
        (L-R, 0, 0.41421356),
        (L, R, 0),
        (L, W-R, 0.41421356),
        (L-R, W, 0),
        (R, W, 0.41421356),
        (0, W-R, 0)
    ], format='xyb', close=True)

    x_pos = [offset_x + (i * (L - 2*offset_x) / 4) for i in range(5)]
    y_pos = [offset_y, W - offset_y]

    for y in y_pos:
        for x in x_pos:
            msp.add_circle((x, y), radius=furo_d/2)

    out_bytes = BytesIO()
    out_text_wrapper = TextIOWrapper(out_bytes, encoding='cp1252', write_through=True)
    doc.write(out_text_wrapper)
    out_text_wrapper.flush()

    return out_bytes.getvalue()

# =========================
# INTERFACE
# =========================
st.title("📏 Gerador de Chapa")

comp = st.number_input("Comprimento (mm):", min_value=300, value=1500)

dxf = gerar_dxf_perfeito(comp)

st.download_button("📥 Baixar DXF", dxf, "chapa.dxf")

# =========================
# AUTO ATUALIZAÇÃO (10s)
# =========================
time.sleep(10)
st.rerun()

import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import io

def extrair_armaduras_por_peca(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()

    armaduras = []
    pecas = re.findall(r"\b([A-Z]{2,6})\b", texto)
    pecas_unicas = list(set(pecas))

    for peca in pecas_unicas:
        padrao_armadura = re.findall(rf"({peca})[^\n]*?(N\d+)\s*[^\n]*?%%c\s*(\d+(\.\d+)?)\s*[^\n]*?(C[=/]\d+|C=\d+)", texto)
        for item in padrao_armadura:
            armaduras.append({
                "Peça": item[0],
                "Referência": item[1],
                "Bitola (mm)": item[2],
                "Espaçamento/Comprimento": item[4]
            })
    return armaduras

st.title("🔍 Extrator de Armaduras por Peça (N)")
st.write("Faça upload de um PDF de detalhamento estrutural para extrair automaticamente os dados de armaduras.")

uploaded_file = st.file_uploader("Envie um arquivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Extraindo dados..."):
        dados = extrair_armaduras_por_peca(uploaded_file)
        if dados:
            df = pd.DataFrame(dados)
            st.success("✅ Extração concluída!")
            st.dataframe(df)

            # Download do CSV
            csv = df.to_csv(sep=";", index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name="valores_N_por_peca.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhuma armadura (N) encontrada no PDF.")

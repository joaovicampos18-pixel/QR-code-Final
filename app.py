"""
 app.py - Interface Streamlit (apenas UI, sem lógica de negócio)
 Execute com: streamlit run app.py
 """
 import logging
 import streamlit as st

from db import conectar, buscar_ultimo_codigo, registrar_lote
 from label_generator import (
 gerar_etiqueta_pequena,
 gerar_etiqueta_larga,
 gerar_pdf_lote,
 gerar_pdf_larga,
 )

# ── Configuração ────────────────────────────────────────────────────────────
 logging.basicConfig(level=logging.INFO)
 st.set_page_config(page_title="Gerador QR - J.V.C.L. Silva", layout="wide")

# ── Estilo ──────────────────────────────────────────────────────────────────
 st.markdown("""
 <style>
 .dev {
 font-size: 16px;
 color: white;
 background: #4A90E2;
 padding: 10px 16px;
 border-radius: 6px;
 margin-bottom: 20px;
 font-weight: bold;
 }
 .stMetric { background: #f0f4ff; border-radius: 8px; padding: 8px; }
 </style>
 <div class="dev">Desenvolvido por: Joao Vitor de Campos Leandro Silva | 2026</div>
 """, unsafe_allow_html=True)

# ── Conexão (cache para não reconectar a cada rerun) ────────────────────────
 @st.cache_resource
 def get_db():
 db = conectar()
 if db is None:
 st.error("❌ Não foi possível conectar ao banco. Verifique o arquivo .env")
 return db

db = get_db()

# ── Estado: próximo código ───────────────────────────────────────────────────
 if "proximo" not in st.session_state:
 st.session_state.proximo = (buscar_ultimo_codigo(db) + 1) if db else 1

px = st.session_state.proximo
 st.metric("Próximo Código", f"{px:08d}")

# ── Abas ─────────────────────────────────────────────────────────────────────
 t1, t2, t3, t4 = st.tabs(["🔢 Auto", "✏️ Manual", "📋 Lista", "📏 Larga"])

# ── ABA AUTO ─────────────────────────────────────────────────────────────────
 with t1:
 qtd = st.number_input("Quantidade de etiquetas:", min_value=1, max_value=200, value=10)
 st.image(gerar_etiqueta_pequena(f"{px:08d}"), width=400, caption="Prévia do primeiro código")

 if st.button("🚀 Gerar Lote", key="btn_auto"):
 codigos = [f"{(px + i):08d}" for i in range(qtd)]

 with st.spinner("Gerando PDF..."):
 pdf_bytes = gerar_pdf_lote(codigos)

 ok = registrar_lote(db, px, px + qtd - 1, qtd) if db else False
 if not ok:
 st.warning("⚠️ PDF gerado, mas não foi possível registrar no banco.")
 else:
 st.session_state.proximo = px + qtd
 st.success(f"✅ {qtd} etiquetas geradas!")

 st.download_button("📥 Download PDF", pdf_bytes, "lote.pdf", mime="application/pdf")

# ── ABA MANUAL ───────────────────────────────────────────────────────────────
 with t2:
 codigo_manual = st.text_input("Digite o código:", key="manual_input")
 if codigo_manual:
 st.image(gerar_etiqueta_pequena(codigo_manual), width=400, caption="Prévia")
 if st.button("🚀 Gerar Manual", key="btn_manual"):
 with st.spinner("Gerando PDF..."):
 pdf_bytes = gerar_pdf_lote([codigo_manual])
 st.download_button("📥 Download PDF", pdf_bytes, "manual.pdf", mime="application/pdf")

# ── ABA LISTA ─────────────────────────────────────────────────────────────────
 with t3:
 st.caption("Cole um código por linha")
 lista_raw = st.text_area("Lista de códigos:", height=200, key="lista_input")
 codigos_lista = [c.strip() for c in lista_raw.splitlines() if c.strip()]

 if codigos_lista:
 st.info(f"{len(codigos_lista)} código(s) detectado(s)")
 st.image(gerar_etiqueta_pequena(codigos_lista[0]), width=400, caption="Prévia do primeiro")

 if st.button("🚀 Gerar Lista", key="btn_lista"):
 with st.spinner("Gerando PDF..."):
 pdf_bytes = gerar_pdf_lote(codigos_lista)
 st.download_button("📥 Download PDF", pdf_bytes, "lista.pdf", mime="application/pdf")

# ── ABA LARGA ─────────────────────────────────────────────────────────────────
 with t4:
 st.caption("Cole os códigos (7 por folha, um por linha)")
 larga_raw = st.text_area("Códigos:", height=200, key="larga_input")
 itens_larga = [e.strip() for e in larga_raw.splitlines() if e.strip()]

 if itens_larga:
 def prefixo(codigo):
 """Retorna tudo antes do último ponto, ex: '01N.014.3' → '01N.014'"""
 partes = codigo.rsplit(".", 1)
 return partes[0] if len(partes) == 2 else codigo

 grupos = []
 grupo_atual = []
 prefixo_atual = None

 for item in itens_larga:
 p = prefixo(item)

 if prefixo_atual is None:
 prefixo_atual = p

 if p != prefixo_atual:
 # Mudou de local: preenche com vazios até completar 7 e fecha
 while len(grupo_atual) < 7:
 grupo_atual.append("")
 grupos.append(grupo_atual)
 grupo_atual = []
 prefixo_atual = p

 grupo_atual.append(item)

 # Grupo cheio com 7 itens: fecha normalmente
 if len(grupo_atual) == 7:
 grupos.append(grupo_atual)
 grupo_atual = []
 prefixo_atual = None

 # Fecha o último grupo incompleto
 if grupo_atual:
 while len(grupo_atual) < 7:
 grupo_atual.append("")
 grupos.append(grupo_atual)

 st.info(f"{len(itens_larga)} código(s) → {len(grupos)} folha(s)")
 st.image(gerar_etiqueta_larga(grupos[0]), use_container_width=True, caption="Prévia da primeira folha")

 if st.button("🚀 Gerar Larga", key="btn_larga"):
 with st.spinner("Gerando PDF..."):
 pdf_bytes = gerar_pdf_larga(grupos)
 st.download_button("📥 Download PDF", pdf_bytes, "larga.pdf", mime="application/pdf")

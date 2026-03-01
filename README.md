# Gerador de Etiquetas QR Code
**Desenvolvido por: Joao Vitor de Campos Leandro Silva | 2026**

## Estrutura do Projeto

```
qr_etiquetas/
├── app.py               # Interface Streamlit (UI)
├── db.py                # Conexão e queries ao Supabase
├── label_generator.py   # Geração de QR codes, imagens e PDFs
├── .env                 # Credenciais (NÃO commitar no Git!)
├── .env.example         # Modelo do .env
└── requirements.txt     # Dependências
```

## Configuração

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciais
Copie o `.env.example` para `.env` e preencha:
```bash
cp .env.example .env
```

Edite o `.env`:
```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anonima-aqui
```

> ⚠️ **NUNCA** coloque as credenciais diretamente no código.  
> ⚠️ **NUNCA** suba o `.env` para o GitHub (adicione ao `.gitignore`).

### 3. Executar
```bash
streamlit run app.py
```

## Deploy no Streamlit Cloud
No painel do Streamlit Cloud, vá em **Settings → Secrets** e adicione:
```toml
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua-chave-anonima-aqui"
```

## O que mudou em relação à versão anterior

| Problema anterior | Solução aplicada |
|---|---|
| Credenciais expostas no código | Variáveis de ambiente via `.env` |
| Tudo em um arquivo só | Separado em `app.py`, `db.py`, `label_generator.py` |
| `except` silenciosos | Logging com mensagens de erro claras |
| Fonte recarregada a cada etiqueta | Cache com `@lru_cache` |
| Sem feedback ao usuário | Spinners, mensagens de sucesso/erro, contagem de itens |
| Reconexão ao banco a cada rerun | `@st.cache_resource` mantém conexão única |

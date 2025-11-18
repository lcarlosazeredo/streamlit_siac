# criar: python -m venv .venv
# atiivar: .venv\Scripts\activate
#instalando o que tme em requirements: python -m pip install -r requirements.txt


# !python -m streamlit run visu.py
# python -m streamlit run visu.py
# app.py (FINAL + RAG)
import streamlit as st
import pandas as pd
import os # <-- NOVO


# --- NOVOS IMPORTS PARA O LLM ---
import os
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
#from langchain.chains import RetrievalQA

# Configuração da página
st.set_page_config(page_title="Análise SIAC (CT)", layout="wide")

# --- NOME DO SEU FICHEIRO MESTRE ---
# MODIFICADO: Mudei para um caminho relativo. 
# Garanta que o CSV está na MESMA PASTA que este script .py
ARQUIVO_MESTRE = "BASE_MESTRE_SIAC_CT_FINAL.csv"

# --- NOVO: CONFIGURAR O LLM (LÊ DO ARQUIVO .streamlit/secrets.toml) ---
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    #llm = GoogleGenerativeAI(model="gemini-1.5-pro-latest")
    #llm = GoogleGenerativeAI(model="gemini-pro")
    #llm = GoogleGenerativeAI(model="gemini-1.0-pro")
    #llm = GoogleGenerativeAI(model="models/gemini-pro-latest")
    llm = GoogleGenerativeAI(model="gemini-pro-latest")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
except Exception as e:
    st.error(f"Erro ao configurar a API do Google. Verifique seu .streamlit/secrets.toml: {e}")
    st.stop() # Impede o app de rodar sem API




# --- CARREGAR OS NOSSO DADOS ---
@st.cache_data
def carregar_dados(nome_arquivo):
    try:
        # Tenta carregar com o caminho relativo
        df = pd.read_csv(nome_arquivo, sep='\t')
        
        # MODIFICADO: Adicionei 'titulo' e 'autores' para o RAG
        colunas_para_limpar = ['tema', 'modalidade', 'area_principal', 'resumo', 
                             'bibliografia', 'local', 'titulo', 'autores']
                             
        for col in colunas_para_limpar:
            if col in df.columns:
                df[col] = df[col].fillna("Não Definido")
        return df
    
    except FileNotFoundError:
        st.error(f"ERRO: Ficheiro '{nome_arquivo}' não encontrado.")
        st.error("Verifique se o nome do arquivo (ARQUIVO_MESTRE) está correto e na mesma pasta do app.py.")
        return pd.DataFrame()

# --- NOVO: CRIAR O BANCO DE DADOS VETORIAL (RAG) ---
@st.cache_resource
def criar_indice_vetorial(_df):
    if _df.empty:
        return None
        
    # 1. Preparar os "Documentos"
    documentos = []
    for _, row in _df.iterrows():
        texto = f"""
        ID do Artigo: {row['id']}
        Título: {row['titulo']}
        Autores: {row['autores']}
        Modalidade: {row['modalidade']}
        Tema: {row['tema']}
        Área: {row['area_principal']}
        Resumo: {row['resumo']}
        """
        doc = Document(
            page_content=texto,
            metadata={"id": str(row['id']), "source": ARQUIVO_MESTRE}
        )
        documentos.append(doc)

    # 2. Criar e Salvar o Índice FAISS (SEM UI)
    try:
        vector_index = FAISS.from_documents(documentos, embeddings)
        return vector_index # Retorna o índice pronto
    except Exception as e:
        # Retorna a exceção para o código principal tratar
        print(f"ERRO GRAVE NO CACHE: {e}") # Log para o terminal
        return e # Retorna o objeto do erro


# 1. Carregamos os dados PRIMEIRO
df = carregar_dados(ARQUIVO_MESTRE)

# 2. NOVO: Criamos o índice (com a UI do lado de fora)
vector_index = None # Inicializa como nulo

with st.spinner("Indexando base de dados para o assistente de IA... (só na primeira vez)"):
    # Chamamos a função cacheada aqui dentro
    indice_ou_erro = criar_indice_vetorial(df)

# 3. Verificamos o que a função retornou
if isinstance(indice_ou_erro, Exception):
    # Se a função retornou um erro, mostramos aqui
    st.error(f"Erro ao criar índice vetorial (pode ser a API): {indice_ou_erro}")
elif indice_ou_erro is not None:
    # Se deu certo, guardamos o índice e mostramos o toast
    vector_index = indice_ou_erro
    st.toast("Assistente de IA pronto!", icon="🤖")
else:
    # Se retornou None (provavelmente df vazio), não faz nada
    pass

# --- TÍTULO DO APP ---
st.title("🔬 Análise de Trabalhos - SIAC 2025 (Centro de Tecnologia)")

if not df.empty:
    # Ordenando o DataFrame pelo 'id'
    if 'id' in df.columns:
        df['id'] = pd.to_numeric(df['id'], errors='coerce')
        df = df.sort_values(by='id').reset_index(drop=True)
   
    st.write(f"Base de dados do CT com {len(df)} trabalhos analisados.")
    
    # --- FILTROS (Seu código original) ---
    st.sidebar.header("Filtros") 
    
    temas_unicos = ['Todos'] + sorted(df['tema'].unique())
    tema_selecionado = st.sidebar.selectbox("Filtrar por Tema da Sessão:", temas_unicos)

    modalidades_unicas = ['Todas'] + sorted(df['modalidade'].unique())
    modalidade_selecionada = st.sidebar.selectbox("Filtrar por Modalidade:", modalidades_unicas)
    
    areas_unicas = ['Todas'] + sorted(df['area_principal'].unique())
    area_selecionada = st.sidebar.selectbox("Filtrar por Área Principal:", areas_unicas)

    locais_unicos = ['Todos'] + sorted(df['local'].unique())
    local_selecionado = st.sidebar.selectbox("Filtrar por Local:", locais_unicos)

    termo_busca = st.sidebar.text_input("Buscar por Título ou Autor:")

    # --- LÓGICA DE FILTRAGEM (Seu código original) ---
    df_filtrado = df.copy() 
    
    if tema_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tema'] == tema_selecionado]
    
    if modalidade_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['modalidade'] == modalidade_selecionada]
        
    if area_selecionada != 'Todas': 
        df_filtrado = df_filtrado[df_filtrado['area_principal'] == area_selecionada]
    
    if local_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['local'] == local_selecionado]
    
    if termo_busca:
        df_filtrado = df_filtrado[
            df_filtrado['titulo'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['autores'].str.contains(termo_busca, case=False, na=False)
        ]

    # --- EXIBIR OS RESULTADOS (Seu código original) ---
    st.header(f"Resultados: {len(df_filtrado)} trabalhos encontrados")
    
    # --- MÉTRICAS (KPIs) (Seu código original) ---
    if not df_filtrado.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temas", df_filtrado['tema'].nunique())
        col2.metric("Áreas", df_filtrado['area_principal'].nunique())
        col3.metric("Modalidades", df_filtrado['modalidade'].nunique())
        col4.metric("Locais", df_filtrado['local'].nunique())
    
    st.write("---") # Adiciona uma linha divisória
    
    # --- MODIFICADO: ABAS (TABS) ---
    # Adicionei a 'tab_ia'
    tab_graficos, tab_tabela, tab_ia = st.tabs([
        "📊 Visão Geral (Gráficos)", 
        "📑 Tabela e Resumos", 
        "🤖 Assistente de IA"
    ])

    # --- SUA ABA DE GRÁFICOS (Seu código original) ---
    with tab_graficos:
        if not df_filtrado.empty:
            st.subheader("Gráficos Rápidos")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Trabalhos por Tema")
                contagem_temas = df_filtrado['tema'].value_counts()
                st.bar_chart(contagem_temas)

            with col2:
                st.write("Trabalhos por Modalidade")
                contagem_modalidade = df_filtrado['modalidade'].value_counts()
                st.bar_chart(contagem_modalidade)
            # --- ADICIONE ESTE NOVO GRÁFICO AQUI ---
            st.write("---")
            st.subheader("Top 10 Orientadores (por nº de trabalhos)")
            
            # Limpeza: Alguns orientadores podem ser "Não Definido"
            orientadores_limpos = df_filtrado[df_filtrado['orientadores'] != "Não Definido"]
            
            if not orientadores_limpos.empty:
                # O "Arquivista" (Pandas) fazendo a contagem
                contagem_orientadores = orientadores_limpos['orientadores'].value_counts().head(10)
                st.bar_chart(contagem_orientadores)
            else:
                st.write("Nenhum orientador definido nos dados filtrados.")
            # --- FIM DO NOVO GRÁFICO ---
        else:
            st.write("Nenhum dado selecionado para exibir gráficos.")

    # --- SUA ABA DE TABELA E RESUMOS (Seu código original) ---
    with tab_tabela:
        # --- TABELA DE DADOS ---
        st.subheader("Dados Filtrados")
        colunas_para_exibir = [
            'id', 'titulo', 'autores', 'orientadores', 'modalidade', 
            'tema', 'area_principal', 'data', 'horario', 'local'
        ]
        colunas_finais = [col for col in colunas_para_exibir if col in df_filtrado.columns]
        st.dataframe(df_filtrado[colunas_finais])
        
        # --- MOSTRAR O RESUMO ---
        if not df_filtrado.empty:
            st.write("---")
            st.header("Ver detalhes do Resumo")
            
            try:
                # 1. Criar a coluna combinada
                df_filtrado['id_e_titulo'] = df_filtrado['id'].astype(str) + " - " + df_filtrado['titulo']
                
                # 2. Usar essa nova coluna como as opções do selectbox
                lista_opcoes = df_filtrado['id_e_titulo'].unique()
                opcao_selecionada = st.selectbox("Selecione um trabalho para ler o resumo:", lista_opcoes)
                
                # 3. Encontrar o trabalho
                if opcao_selecionada:
                    trabalho_detalhe = df_filtrado[df_filtrado['id_e_titulo'] == opcao_selecionada].iloc[0]
                    
                    st.subheader(trabalho_detalhe['titulo'])
                    st.write(f"**Autores:** {trabalho_detalhe['autores']}")
                    st.write(f"**Orientadores:** {trabalho_detalhe['orientadores']}")
                    
                    st.write(f"**Resumo:**")
                    st.info(trabalho_detalhe['resumo'])
                    
                    if 'bibliografia' in trabalho_detalhe and trabalho_detalhe['bibliografia'] != "Não Definido":
                        st.write("**Bibliografia:**")
                        st.caption(trabalho_detalhe['bibliografia'])
            except Exception as e:
                st.warning(f"Não foi possível exibir os detalhes do resumo. (Nenhum trabalho selecionado? {e})")
         
    # --- NOVO: ABA DO ASSISTENTE DE IA ---
    # --- NOVO: ABA DO ASSISTENTE DE IA (Versão Manual) ---
        with tab_ia:
            st.header("🤖 Converse com os Resumos")
            #st.write("Faça perguntas em linguagem natural sobre os trabalhos (ex: 'Quais trabalhos mencionam biologia?' ou 'Liste os resumos sobre engenharia civil').")
            st.write("Faça perguntas em linguagem natural sobre os trabalhos.")
            st.info("Nota: O assistente usa a base de dados *completa*, não os dados filtrados na barra lateral.")
            
            pergunta_usuario = st.text_input("Sua pergunta:")
            
            # Esta é a nova lógica "manual" que não usa langchain.chains
            if pergunta_usuario and vector_index:
                with st.spinner("Buscando e pensando..."):
                    try:
                        # 1. BUSCAR (Retrieve)
                        # Cria o "buscador" a partir do seu índice
                        retriever = vector_index.as_retriever(search_kwargs={"k": 4})
                        
                        # Busca os 4 documentos mais relevantes para a pergunta
                        docs_relevantes = retriever.invoke(pergunta_usuario)
                        
                        # 2. FORMATAR (Format)
                        # Junta o texto dos documentos relevantes
                        contexto = "\n\n---\n\n".join(doc.page_content for doc in docs_relevantes)
                        
                        # Cria o prompt que enviaremos ao Gemini
                        prompt_formatado = f"""
                        Você é um assistente de IA. Responda à pergunta do usuário baseado *apenas* no contexto fornecido abaixo.
                        Se a resposta não estiver no contexto, diga "Não encontrei essa informação nos resumos".
    
                        **Contexto Fornecido:**
                        {contexto}
    
                        **Pergunta do Usuário:**
                        {pergunta_usuario}
    
                        **Sua Resposta:**
                        """
                        
                        # 3. PERGUNTAR (Generate)
                        # Chama o Gemini diretamente com o prompt
                        resposta = llm.invoke(prompt_formatado)
                        
                        # Exibe a resposta
                        st.markdown(resposta)
                        
                        # Opcional: Mostrar quais documentos ele usou
                        with st.expander("Ver fontes (contexto) usadas pela IA"):
                            if docs_relevantes:
                                for doc in docs_relevantes:
                                    st.info(f"**ID:** {doc.metadata.get('id', 'N/A')}\n\n{doc.page_content[:500]}...")
                            else:
                                st.write("Nenhum documento relevante encontrado.")
    
                    except Exception as e:
                        st.error(f"Erro ao processar a pergunta: {e}")
            
            elif not vector_index:
                st.error("O índice vetorial não foi carregado. O assistente de IA está desativado.")

# --- FIM DO IF (Seu código original) ---
else:

    st.warning("A base de dados não foi carregada. Verifique os erros acima.")

# python -m streamlit run visuuio.py
# app.py (FINAL)

import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Análise SIAC (CT)", layout="wide")

# --- NOME DO SEU FICHEIRO MESTRE ---
ARQUIVO_MESTRE = r"C:\Users\lcarl\Desktop\PSIAC6\BASE_MESTRE_SIAC_CT_FINAL.csv"




# --- CARREGAR OS NOSSOS DADOS ---
@st.cache_data
def carregar_dados(nome_arquivo):
    try:
        df = pd.read_csv(nome_arquivo, sep='\t')
        
        # Limpeza para os filtros e para a exibição
        for col in ['tema', 'modalidade', 'area_principal', 'resumo', 'bibliografia', 'local']:
            if col in df.columns:
                df[col] = df[col].fillna("Não Definido")
        return df
    
    except FileNotFoundError:
        st.error(f"ERRO: Ficheiro '{nome_arquivo}' não encontrado.")
        st.error("Verifique se o nome do arquivo (ARQUIVO_MESTRE) está correto e na mesma pasta do app.py.")
        return pd.DataFrame()




# 1. Carregamos os dados PRIMEIRO
df = carregar_dados(ARQUIVO_MESTRE)

# --- TÍTULO DO APP ---
st.title("🔬 Análise de Trabalhos - SIAC 2025 (Centro de Tecnologia)")

if not df.empty:
    #Ordenando o DataFrame pelo 'id'
    if 'id' in df.columns:
        # Converter 'id' para número para ordenar
        df['id'] = pd.to_numeric(df['id'], errors='coerce')
        # Ordenar o DataFrame inteiro pelo 'id'
        df = df.sort_values(by='id').reset_index(drop=True)
   
    st.write(f"Base de dados do CT mestre com {len(df)} trabalhos analisados.")
    
    # --- FILTROS ---
    st.sidebar.header("Filtros") 
    
    temas_unicos = ['Todos'] + sorted(df['tema'].unique())
    tema_selecionado = st.sidebar.selectbox("Filtrar por Tema da Sessão:", temas_unicos)

    modalidades_unicas = ['Todas'] + sorted(df['modalidade'].unique())
    modalidade_selecionada = st.sidebar.selectbox("Filtrar por Modalidade:", modalidades_unicas)
    
    areas_unicas = ['Todas'] + sorted(df['area_principal'].unique())
    area_selecionada = st.sidebar.selectbox("Filtrar por Área Principal:", areas_unicas)

    locais_unicos = ['Todos'] + sorted(df['local'].unique())
    local_selecionado = st.sidebar.selectbox("Filtrar por Local:", locais_unicos)

    termo_busca = st.sidebar.text_input("Buscar por Título ou Autor:")# Busca no título OU nos autores

    # --- LÓGICA DE FILTRAGEM ---
    df_filtrado = df.copy() 
    
    if tema_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tema'] == tema_selecionado]
    
    if modalidade_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['modalidade'] == modalidade_selecionada]
        
    if area_selecionada != 'Todas': 
        df_filtrado = df_filtrado[df_filtrado['area_principal'] == area_selecionada]
    
    if local_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['local'] == local_selecionado]
    
    if termo_busca:# Busca no título OU nos autores
        # Busca no título OU nos autores (sem diferenciar maiúsculas/minúsculas)
        df_filtrado = df_filtrado[
            df_filtrado['titulo'].str.contains(termo_busca, case=False, na=False) |
            df_filtrado['autores'].str.contains(termo_busca, case=False, na=False)
        ]

    # --- EXIBIR OS RESULTADOS ---
    st.header(f"Resultados: {len(df_filtrado)} trabalhos encontrados")
    
    # --- NOVO: MÉTRICAS (KPIs) ---################################################
    if not df_filtrado.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temas", df_filtrado['tema'].nunique())
        col2.metric("Áreas", df_filtrado['area_principal'].nunique())
        col3.metric("Modalidades", df_filtrado['modalidade'].nunique())
        col4.metric("Locais", df_filtrado['local'].nunique())
    
    st.write("---") # Adiciona uma linha divisória
    
    # --- NOVO: ABAS (TABS) ---
    tab1, tab2 = st.tabs(["📊 Visão Geral (Gráficos)", "📑 Tabela e Resumos"])

    with tab1:
        # --- GRÁFICOS ---
        if not df_filtrado.empty:
            st.subheader("Gráficos Rápidos")
            col1, col2 = st.columns(2)
            with col1:
                st.write("Trabalhos por Tema")
                # ... (seu código de gráfico 1) ...
                st.write("Trabalhos por Tema")
                contagem_temas = df_filtrado['tema'].value_counts()
                st.bar_chart(contagem_temas)

            with col2:
                st.write("Trabalhos por Modalidade")
                # ... (seu código de gráfico 2) ...
                st.write("Trabalhos por Modalidade")
                contagem_modalidade = df_filtrado['modalidade'].value_counts()
                st.bar_chart(contagem_modalidade)
            # (Você pode adicionar mais gráficos aqui)
            
        else:
            st.write("Nenhum dado selecionado para exibir gráficos.")

    with tab2:
        # --- TABELA DE DADOS ---
        st.subheader("Dados Filtrados")
        # ... (seu código do st.dataframe) ...
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
            # ... (todo o seu código do selectbox e exibição do resumo) ...
            # 1. Criar a coluna combinada (ex: "513 - Avaliação do pH...")
            # (Garantir que o ID é string, para o caso de ser lido como número)
            df_filtrado['id_e_titulo'] = df_filtrado['id'].astype(str) + " - " + df_filtrado['titulo']
            
            # 2. Usar essa nova coluna como as opções do selectbox
            lista_opcoes = df_filtrado['id_e_titulo'].unique()
            opcao_selecionada = st.selectbox("Selecione um trabalho para ler o resumo:", lista_opcoes)
            
            # 3. Encontrar o trabalho usando essa coluna combinada
            trabalho_detalhe = df_filtrado[df_filtrado['id_e_titulo'] == opcao_selecionada].iloc[0]
            
            # --- FIM DA MUDANÇA ---
            
            st.subheader(trabalho_detalhe['titulo'])
            st.write(f"**Autores:** {trabalho_detalhe['autores']}")
            st.write(f"**Orientadores:** {trabalho_detalhe['orientadores']}")
            
            st.write(f"**Resumo:**")
            st.info(trabalho_detalhe['resumo'])
            
            # A Bibliografia (já estava correto)
            if 'bibliografia' in trabalho_detalhe and trabalho_detalhe['bibliografia'] != "Não Definido":
                st.write("**Bibliografia:**")
                st.caption(trabalho_detalhe['bibliografia'])

    #######################################################################


















        # --- NOVO: MOSTRAR A BIBLIOGRAFIA (Como pediu) ---
        #if 'bibliografia' in trabalho_detalhe and trabalho_detalhe['bibliografia'] != "Não Definido":
        #    # 'st.expander' cria um menu "clicável"
        #    with st.expander("Ver Bibliografia"):
        #        st.caption(trabalho_detalhe['bibliografia'])
         





else:
    st.warning("A base de dados não foi carregada. Verifique os erros acima.")
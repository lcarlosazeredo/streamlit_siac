# merge.py (CORRIGIDO)
# -----------------------------------------------------------
# SCRIPT 3
# -----------------------------------------------------------
import pandas as pd
import sys

# --- O SEU CAMINHO ---
PASTA_DO_PROJETO = r"C:\Users\lcarl\Desktop\PSIAC6" # <-- Verifique se esta pasta está correta

try:
    # --- FICHEIROS DE ENTRADA (Corrigidos) ---
    arquivo_programacao = PASTA_DO_PROJETO + r"\programacao_siac_ct_FINAL.csv"
    arquivo_resumos = PASTA_DO_PROJETO + r"\resumos_siac_ct_FINAL.csv" 
    
    # --- FICHEIRO DE SAÍDA ---
    arquivo_final_mestre = PASTA_DO_PROJETO + r"\BASE_MESTRE_SIAC_CT_FINAL.csv"

    print("\nSCRIPT 3: Carregando CSVs corrigidos...")
    df_programacao = pd.read_csv(arquivo_programacao) # CSV normal
    df_resumos = pd.read_csv(arquivo_resumos, sep='\t') # CSV com TAB
    
    print(f"-> Programação: {len(df_programacao)} linhas.")
    print(f"-> Resumos: {len(df_resumos)} linhas.")

    df_programacao['id'] = df_programacao['id'].astype(str)
    df_resumos['id'] = df_resumos['id'].astype(str)
    
    print("Executando a junção 'inner'...")
    df_final = pd.merge(
        df_programacao, 
        df_resumos, 
        on="id", 
        how="inner", # 'inner' junta só os que estão em AMBOS
        suffixes=('_prog', '_resumo')
    )
    print(f"Junção concluída. Resultado: {len(df_final)} linhas.")

    # Limpeza
    colunas_a_remover = []
    if 'autores_orientadores' in df_final.columns: colunas_a_remover.append('autores_orientadores')
    if 'titulo_prog' in df_final.columns: colunas_a_remover.append('titulo_prog')
    df_final = df_final.drop(columns=colunas_a_remover)
    df_final = df_final.rename(columns={"titulo_resumo": "titulo"})
    
    df_final.to_csv(arquivo_final_mestre, index=False, encoding='utf-8-sig', sep='\t')
    
    print(f"\n--- SCRIPT 3: SUCESSO TOTAL ---")
    print(f"Base de dados mestre FINAL salva em: '{arquivo_final_mestre}'")
    
except FileNotFoundError as e:
    print(f"\n--- SCRIPT 3: ERRO ---")
    print(f"Ficheiro não encontrado: {e.filename}")
except Exception as e:
    print(f"SCRIPT 3: Ocorreu um erro inesperado: {e}")
# merge.py (VERSÃO FUNÇÃO - UNIFICA AS BASES)
# -----------------------------------------------------------
# SCRIPT 3
# -----------------------------------------------------------
import pandas as pd
import os

PASTA_DO_PROJETO = os.getcwd() # Pega a pasta atual


def processar_merge(sigla):
    print(f"\n--- [MERGE] Iniciando unificação para: {sigla} ---")
    
    nome_min = sigla.lower()
    nome_mai = sigla.upper() 

    # Define os caminhos dos arquivos
    arquivo_programacao = os.path.join(PASTA_DO_PROJETO, "pdfs", f"programacao_siac_{nome_min}_FINAL.csv")
    arquivo_resumos = os.path.join(PASTA_DO_PROJETO, "pdfs", f"resumos_siac_{nome_min}_FINAL.csv")
    
    # Define o arquivo de saída
    arquivo_final_mestre = os.path.join(PASTA_DO_PROJETO, "pdfs", f"BASE_MESTRE_SIAC_{nome_mai}_FINAL.csv")

    try:
        # Carregar CSVs
        df_programacao = pd.read_csv(arquivo_programacao) 
        df_resumos = pd.read_csv(arquivo_resumos, sep='\t') 
        
        # Garantir que ID é string para o merge funcionar
        df_programacao['id'] = df_programacao['id'].astype(str)
        df_resumos['id'] = df_resumos['id'].astype(str)
        
        # Executar a junção 'inner'
        df_final = pd.merge(
            df_programacao, 
            df_resumos, 
            on="id", 
            how="inner", # 'inner' junta só os que estão em AMBOS
            suffixes=('_prog', '_resumo')
        )
        
        # --- CRIA COLUNA DE ORIGEM ---
        df_final['origem'] = nome_mai
        # -----------------------------

        # Limpeza
        colunas_a_remover = []
        if 'autores_orientadores' in df_final.columns: colunas_a_remover.append('autores_orientadores')
        if 'titulo_prog' in df_final.columns: colunas_a_remover.append('titulo_prog')
        
        df_final = df_final.drop(columns=colunas_a_remover)
        df_final = df_final.rename(columns={"titulo_resumo": "titulo"})
        
        # Reordenar colunas para 'origem' aparecer logo no início
        cols = list(df_final.columns)
        if 'origem' in cols:
            cols.insert(1, cols.pop(cols.index('origem'))) # Move 'origem' para a segunda posição
            df_final = df_final[cols]

        # Salvar o arquivo final
        df_final.to_csv(arquivo_final_mestre, index=False, encoding='utf-8-sig', sep='\t')
        
        print(f"   [OK] Base unificada: {len(df_final)} linhas. Salvo em: BASE_MESTRE_SIAC_{nome_mai}_FINAL.csv")
        return True
        
    except FileNotFoundError as e:
        print(f"   [ERRO] Arquivo CSV não encontrado: {e.filename}")
        print(f"   Dica: Verifique se você já rodou os scripts de extração para '{sigla}'.")
        return False
    except Exception as e:
        print(f"   [ERRO] Falha no merge ({sigla}): {e}")
        return False

# Bloco para teste 
if __name__ == "__main__":
    processar_merge("CT")
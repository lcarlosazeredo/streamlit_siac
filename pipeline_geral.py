# pipeline_geral.py
# -----------------------------------------------------------
# SCRIPT 4
# -----------------------------------------------------------
import os
import pandas as pd
import time


try:
    from new_extrac_sessoes import processar_sessoes
    from new_extrac_resumos import processar_resumos
    from new_merge import processar_merge
except ImportError:
    print("ERRO: Não foi possível importar os scripts. Verifique se você criou as funções 'def' dentro deles.")
    exit()

LISTA_ORIGENS = ["CAXIAS", "CCJE", "CCMN", "CCS", "CFCH", "CLA", "CT", "FCC", "MACAE"]

PASTA_DO_PROJETO = os.getcwd() # Pega a pasta atual

def main():
    print("=================================================")
    print("   INICIANDO PIPELINE DE DADOS SIAC 2025")
    print(f"   Processando {len(LISTA_ORIGENS)} origens...")
    print("=================================================\n")

    sucessos = []
    falhas = []

    # 1. LOOP PRINCIPAL (Roda os 3 scripts para cada centro)
    for origem in LISTA_ORIGENS:
        start_time = time.time()
        print(f"🔹 PROCESSANDO: {origem}")
        
        try:
            # Passo 1: Sessões
            print(f"   1/3 Extraindo Sessões ({origem})...")
            processar_sessoes(origem)
            
            # Passo 2: Resumos
            print(f"   2/3 Extraindo Resumos ({origem})...")
            processar_resumos(origem)
            
            # Passo 3: Merge
            print(f"   3/3 Unificando Base ({origem})...")
            processar_merge(origem)
            
            sucessos.append(origem)
            print(f"   ✅ {origem} concluído em {round(time.time() - start_time, 2)}s\n")
            
        except Exception as e:
            print(f"   ❌ ERRO em {origem}: {e}")
            falhas.append(origem)
            print("   Pulando para o próximo...\n")

    # 2. Juntar tudo num arquivo só)
    print("=================================================")
    print("   UNIFICANDO TODAS AS BASES EM UMA SÓ")
    print("=================================================")
    
    dfs = []
    for origem in sucessos:
        caminho_csv = os.path.join(PASTA_DO_PROJETO, "pdfs", f"BASE_MESTRE_SIAC_{origem}_FINAL.csv")
        if os.path.exists(caminho_csv):
            try:
                df_temp = pd.read_csv(caminho_csv, sep='\t')
                dfs.append(df_temp)
            except Exception as e:
                print(f"Erro ao ler CSV do {origem}: {e}")
    
    if dfs:
        df_geral = pd.concat(dfs, ignore_index=True)
        
        # Salva o arquivo final com TUDO
        nome_final_geral = "BASE_SIAC_UFRJ_COMPLETA.csv"
        df_geral.to_csv(nome_final_geral, index=False, encoding='utf-8-sig', sep='\t')
        
        print(f"🎉 SUCESSO! Base completa gerada com {len(df_geral)} trabalhos.")
        print(f"📁 Arquivo salvo: {nome_final_geral}")
        
        # Estatísticas rápidas
        print("\nResumo por Origem:")
        print(df_geral['origem'].value_counts())
    else:
        print("Nenhum dado foi processado com sucesso.")

    if falhas:
        print(f"\n⚠️ Atenção: As seguintes origens falharam: {falhas}")

if __name__ == "__main__":
    main()
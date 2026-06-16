import pandas as pd
import numpy as np
import os

def gerar_base_consolidada():
    print('🔄 [ETL ANALYTICS] Iniciando extração e tratamento de dados para o Dashboard...')
    
    # Caminhos dos arquivos (subindo um nível para achar a pasta dataset_olist na raiz)
    caminho_dados = os.path.join('..', 'dataset_olist')
    
    # Fallback caso você execute o script direto da raiz por engano
    if not os.path.exists(caminho_dados):
        caminho_dados = 'dataset_olist'

    try:
        df_sellers = pd.read_csv(f'{caminho_dados}/olist_sellers_dataset.csv')
        df_items = pd.read_csv(f'{caminho_dados}/olist_order_items_dataset.csv')
        df_orders = pd.read_csv(f'{caminho_dados}/olist_orders_dataset.csv')
        df_products = pd.read_csv(f'{caminho_dados}/olist_products_dataset.csv')
        df_reviews = pd.read_csv(f'{caminho_dados}/olist_order_reviews_dataset.csv')
        df_customers = pd.read_csv(f'{caminho_dados}/olist_customers_dataset.csv')
        print('✅ [ETL ANALYTICS] Todas as tabelas carregadas com sucesso!')
    except FileNotFoundError as e:
        print(f'❌ [ERRO] Não foi possível encontrar os arquivos na pasta dataset_olist: {e}')
        return

    # 1. Filtrar vendedores da Bahia
    sellers_ba = df_sellers[df_sellers['seller_state'] == 'BA'].copy()
    lista_ids_vendedores = sellers_ba['seller_id'].unique()
    
    # 2. Filtrar itens vendidos por eles
    vendas_ba = df_items[df_items['seller_id'].isin(lista_ids_vendedores)].copy()
    
    # 3. Cruzar dados para montar o quebra-cabeça analítico
    print('🔄 [ETL ANALYTICS] Cruzando tabelas e aplicando regras de negócio...')
    df_consolidado = pd.merge(vendas_ba, df_orders, on='order_id', how='inner')
    df_consolidado = pd.merge(df_consolidado, df_products, on='product_id', how='left')
    df_consolidado = pd.merge(df_consolidado, df_reviews, on='order_id', how='left')
    df_consolidado = pd.merge(df_consolidado, df_customers, on='customer_id', how='left')
    
    # ✨ CORREÇÃO AQUI: Adicionado 'seller_state' no cruzamento para que a linha abaixo o encontre
    df_consolidado = pd.merge(
        df_consolidado, 
        sellers_ba[['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']], 
        on='seller_id', 
        how='left'
    )

    # 4. Tratamento de Datas e Prazos Logísticos
    colunas_data = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in colunas_data:
        df_consolidado[col] = pd.to_datetime(df_consolidado[col])

    # Filtrar apenas entregues para análise de prazos e criar métricas em dias
    df_consolidado['dias_entrega_real'] = (df_consolidado['order_delivered_customer_date'] - df_consolidado['order_purchase_timestamp']).dt.days
    df_consolidado['dias_prazo_estimado'] = (df_consolidado['order_estimated_delivery_date'] - df_consolidado['order_purchase_timestamp']).dt.days
    df_consolidado['status_prazo'] = np.where(df_consolidado['dias_entrega_real'] > df_consolidado['dias_prazo_estimado'], 'Atrasado', 'No Prazo')
    
    # Tratar pedidos que não foram entregues ainda para não quebrar a média
    df_consolidado.loc[df_consolidado['order_status'] != 'delivered', 'status_prazo'] = 'Não Entregue'

    # 5. O PULO DO GATO: Aplicando a Lógica Logística do Motor de QA
    print('🔀 [ETL ANALYTICS] Classificando rotas logísticas (Metropolitana vs Interior)...')
    
    # Pegamos os 2 primeiros dígitos dos prefixos de CEP de origem e destino
    df_consolidado['origem_macro'] = df_consolidado['seller_zip_code_prefix'].astype(str).str.zfill(5).str[:2]
    df_consolidado['destino_macro'] = df_consolidado['customer_zip_code_prefix'].astype(str).str.zfill(5).str[:2]
    
    # Regra do frete regionalizada desenvolvida no QA
    df_consolidado['rota_logistica'] = np.where(
        (df_consolidado['seller_state'] == 'BA') & (df_consolidado['customer_state'] == 'BA') & (df_consolidado['origem_macro'] == df_consolidado['destino_macro']),
        'Metropolitana (BA)',
        np.where(
            (df_consolidado['seller_state'] == 'BA') & (df_consolidado['customer_state'] == 'BA'),
            'Interior (BA)',
            'Interestadual (Fora da BA)'
        )
    )

    # 6. Limpeza e Padronização de Nomes
    df_consolidado['product_category_name'] = df_consolidado['product_category_name'].fillna('não_informado').str.replace('_', ' ').str.title()
    df_consolidado['customer_city'] = df_consolidado['customer_city'].str.lower().str.strip().str.title()
    df_consolidado['seller_city'] = df_consolidado['seller_city'].str.lower().str.strip().str.title()

    # Selecionar e ordenar apenas colunas estratégicas para o Power BI
    colunas_finais = [
        'order_id', 'product_id', 'seller_id', 'seller_city', 'product_category_name',
        'price', 'freight_value', 'order_purchase_timestamp', 'status_prazo',
        'dias_entrega_real', 'dias_prazo_estimado', 'review_score', 
        'customer_city', 'customer_state', 'rota_logistica'
    ]
    
    base_final = df_consolidado[colunas_finais].copy()

    # Salvar arquivo tratado para o dashboard
    caminho_salvamento = f'{caminho_dados}/base_dashboard_bahia.csv'
    base_final.to_csv(caminho_salvamento, index=False)
    
    print('\n==================================================')
    print('💾 [ETL ANALYTICS] SUCESSO ABSOLUTO!')
    print('==================================================')
    print(f'📊 Base unificada gerada com {len(base_final)} registros.')
    print(f'📂 Arquivo salvo pronto para o Power BI em: {caminho_salvamento}')
    print('==================================================\n')

if __name__ == "__main__":
    gerar_base_consolidada()
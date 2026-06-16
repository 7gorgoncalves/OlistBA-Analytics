import pandas as pd
import numpy as np
import os

def executar_super_diagnostico():
    print('🔄 [MASTER ANALYTICS] Carregando dados nacionais para o super diagnóstico...')
    caminho_dados = os.path.join('..', 'dataset_olist')
    if not os.path.exists(caminho_dados):
        caminho_dados = 'dataset_olist'

    try:
        df_sellers = pd.read_csv(f'{caminho_dados}/olist_sellers_dataset.csv')
        df_items = pd.read_csv(f'{caminho_dados}/olist_order_items_dataset.csv')
        df_orders = pd.read_csv(f'{caminho_dados}/olist_orders_dataset.csv')
        df_products = pd.read_csv(f'{caminho_dados}/olist_products_dataset.csv')
        df_customers = pd.read_csv(f'{caminho_dados}/olist_customers_dataset.csv')
        df_reviews = pd.read_csv(f'{caminho_dados}/olist_order_reviews_dataset.csv')
        print('✅ Tabelas carregadas! Iniciando cruzamentos em nível nacional e estadual...\n')
    except FileNotFoundError as e:
        print(f'❌ Erro ao ler arquivos: {e}')
        return

    # Padronização inicial
    df_products['product_category_name'] = df_products['product_category_name'].fillna('Não Informado').str.replace('_', ' ').str.title()
    df_customers['customer_city'] = df_customers['customer_city'].str.title().str.strip()
    df_sellers['seller_city'] = df_sellers['seller_city'].str.title().str.strip()

    # Base Nacional Completa (Merge dos itens com compradores e vendedores)
    df_br = pd.merge(df_items, df_orders, on='order_id', how='inner')
    df_br = pd.merge(df_br, df_customers, on='customer_id', how='left')
    df_br = pd.merge(df_br, df_sellers, on='seller_id', how='left')
    df_br = pd.merge(df_br, df_products, on='product_id', how='left')
    df_br = pd.merge(df_br, df_reviews, on='order_id', how='left')

    # Datas
    df_br['order_purchase_timestamp'] = pd.to_datetime(df_br['order_purchase_timestamp'])
    df_br['order_delivered_customer_date'] = pd.to_datetime(df_br['order_delivered_customer_date'])
    df_br['lead_time'] = (df_br['order_delivered_customer_date'] - df_br['order_purchase_timestamp']).dt.days

    # Faturamento Total Brasil
    fat_total_br = df_br['price'].sum()

    # =========================================================================
    # 1 & 2. POSIÇÃO DA BAHIA NO BRASIL (VENDA E COMPRA)
    # =========================================================================
    vendas_vendedor_ba = df_br[df_br['seller_state'] == 'BA']
    compras_cliente_ba = df_br[df_br['customer_state'] == 'BA']

    fat_vendas_ba = vendas_vendedor_ba['price'].sum()
    fat_compras_ba = compras_cliente_ba['price'].sum()

    share_venda_ba = (fat_vendas_ba / fat_total_br) * 100
    share_compra_ba = (fat_compras_ba / fat_total_br) * 100

    print('==================================================')
    print('📊 1. POSIÇÃO DA BAHIA NO MARKET SHARE NACIONAL')
    print('==================================================')
    print(f'🏭 COMO POLO VENDEDOR: R$ {fat_vendas_ba:,.2f} ({share_venda_ba:.2f}% do e-commerce nacional)')
    print(f'🛒 COMO POLO COMPRADOR: R$ {fat_compras_ba:,.2f} ({share_compra_ba:.2f}% do e-commerce nacional)')

    # =========================================================================
    # 3 & 4. TICKETS MÉDIOS (COMPRA E VENDA DA BA)
    # =========================================================================
    ticket_medio_venda_ba = vendas_vendedor_ba.groupby('order_id')['price'].sum().mean()
    ticket_medio_compra_ba = compras_cliente_ba.groupby('order_id')['price'].sum().mean()

    print('\n==================================================')
    print('🎟️ 2. TICKETS MÉDIOS DO ECOSSISTEMA BAIANO')
    print('==================================================')
    print(f'💰 Ticket Médio quando a BA VENDE : R$ {ticket_medio_venda_ba:,.2f}')
    print(f'🛍️ Ticket Médio quando a BA COMPRA: R$ {ticket_medio_compra_ba:,.2f}')

    # =========================================================================
    # 5 & 6. TOP 5 CIDADES QUE MAIS COMPRAM E VENDEM (DENTRO DA BA)
    # =========================================================================
    print('\n==================================================')
    print('🏙️ 3. TOP 5 CIDADES INTERNAS DA BAHIA (VOLUME FINANCEIRO)')
    print('==================================================')
    print('🏭 TOP 5 CIDADES MAIS VENDEDORAS DA BA:')
    top_cidades_vendem = vendas_vendedor_ba.groupby('seller_city')['price'].sum().sort_values(ascending=False).head(5)
    for i, (cidade, fat) in enumerate(top_cidades_vendem.items(), 1):
        print(f'   {i}º {cidade:<20} ↳ Faturamento: R$ {fat:,.2f}')

    print('\n🛒 TOP 5 CIDADES MAIS COMPRADORAS DA BA:')
    top_cidades_compram = compras_cliente_ba.groupby('customer_city')['price'].sum().sort_values(ascending=False).head(5)
    for i, (cidade, fat) in enumerate(top_cidades_compram.items(), 1):
        print(f'   {i}º {cidade:<20} ↳ Consumo: R$ {fat:,.2f}')

    # =========================================================================
    # 7 & 8. TOP 5 CIDADES COM MELHORES TICKETS MÉDIOS NA BA (Mínimo de 3 pedidos para evitar outliers de 1 compra)
    # =========================================================================
    print('\n==================================================')
    print('💎 4. TOP 5 CIDADES DA BA COM MAIOR TICKET MÉDIO')
    print('==================================================')
    
    # Filtro de volume mínimo para o ticket médio fazer sentido estatístico
    vendas_cidade_filtro = vendas_vendedor_ba.groupby('seller_city').filter(lambda x: x['order_id'].nunique() >= 2)
    compras_cidade_filtro = compras_cliente_ba.groupby('customer_city').filter(lambda x: x['order_id'].nunique() >= 5)

    print('🏭 MELHORES TICKETS MÉDIOS DE VENDA (Cidades Produtoras):')
    ticket_venda_cidade = vendas_cidade_filtro.groupby('seller_city').agg(
        tk_med=('price', lambda x: x.sum() / vendas_cidade_filtro.loc[x.index, 'order_id'].nunique())
    ).sort_values(by='tk_med', ascending=False).head(5)
    for i, row in enumerate(ticket_venda_cidade.itertuples(), 1):
        print(f'   {i}º {row.Index:<20} ↳ Ticket Médio de Venda: R$ {row.tk_med:,.2f}')

    print('\n🛒 MELHORES TICKETS MÉDIOS DE COMPRA (Cidades Consumidoras):')
    ticket_compra_cidade = compras_cidade_filtro.groupby('customer_city').agg(
        tk_med=('price', lambda x: x.sum() / compras_cidade_filtro.loc[x.index, 'order_id'].nunique())
    ).sort_values(by='tk_med', ascending=False).head(5)
    for i, row in enumerate(ticket_compra_cidade.itertuples(), 1):
        print(f'   {i}º {row.Index:<20} ↳ Ticket Médio de Compra: R$ {row.tk_med:,.2f}')

    # =========================================================================
    # 9 & 10. TOP 5 PRODUTOS (CATEGORIAS) MAIS COMPRADOS E VENDIDOS NA BA
    # =========================================================================
    print('\n==================================================')
    print('📦 5. TOP 5 CATEGORIAS DE PRODUTOS NA BAHIA')
    print('==================================================')
    print('🏭 CATEGORIAS MAIS VENDIDAS PELOS LOJISTAS DA BA:')
    top_prod_venda = vendas_vendedor_ba.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(5)
    for i, (cat, fat) in enumerate(top_prod_venda.items(), 1):
        print(f'   {i}º {cat:<25} ↳ Total Comercializado: R$ {fat:,.2f}')

    print('\n🛒 CATEGORIAS MAIS COMPRADAS PELOS CONSUMIDORES DA BA:')
    top_prod_compra = compras_cliente_ba.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(5)
    for i, (cat, fat) in enumerate(top_prod_compra.items(), 1):
        print(f'   {i}º {cat:<25} ↳ Total Consumido: R$ {fat:,.2f}')

    # =========================================================================
    # 11. LEADTIME DE ENTREGA DOS VENDEDORES DA BAHIA POR MICRO-ROTA
    # =========================================================================
    print('\n==================================================')
    print('🚚 6. LEAD TIME MÉDIO DE ENTREGA (VENDEDORES DA BA)')
    print('==================================================')
    
    lead_geral_ba = vendas_vendedor_ba['lead_time'].mean()
    print(f'⏱️ Lead Time Médio Geral de Despacho da BA: {lead_geral_ba:.1f} dias')
    
    # Quebrando o leadtime por tipo de rota para enriquecer a visão logística
    vendas_vendedor_ba = vendas_vendedor_ba.copy()
    vendas_vendedor_ba['origem_m'] = vendas_vendedor_ba['seller_zip_code_prefix'].astype(str).str.zfill(5).str[:2]
    vendas_vendedor_ba['destino_m'] = vendas_vendedor_ba['customer_zip_code_prefix'].astype(str).str.zfill(5).str[:2]
    
    vendas_vendedor_ba['tipo_rota'] = np.where(
        (vendas_vendedor_ba['customer_state'] == 'BA') & (vendas_vendedor_ba['origem_m'] == vendas_vendedor_ba['destino_m']), 'Metropolitana (BA)',
        np.where(vendas_vendedor_ba['customer_state'] == 'BA', 'Interior (BA)', 'Interestadual (Fora da BA)')
    )
    
    lead_por_rota = vendas_vendedor_ba.groupby('tipo_rota')['lead_time'].mean()
    for rota, tempo in lead_por_rota.items():
        print(f'   ↳ Rota {rota:<26}: {tempo:.1f} dias médios')
    print('==================================================\n')

if __name__ == '__main__':
    executar_super_diagnostico()
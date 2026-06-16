import pandas as pd
import numpy as np

def executar_diagnostico_avancado():
    print('📊 [ANALYTICS] Lendo base tratada (base_dashboard_bahia.csv)...')
    
    try:
        df = pd.read_csv('../dataset_olist/base_dashboard_bahia.csv')
    except FileNotFoundError:
        try:
            df = pd.read_csv('dataset_olist/base_dashboard_bahia.csv')
        except FileNotFoundError:
            print('❌ [ERRO] Base tratada não encontrada. Rode o gerar_base_dash.py primeiro!')
            return

    print('✅ Base carregada! Calculando métricas de alto impacto para o terminal...\n')

    # ==================================================
    # Visão Geral do Ecossistema
    # ==================================================
    faturamento_total = df['price'].sum()
    ticket_medio = df.groupby('order_id')['price'].sum().mean()
    total_pedidos = df['order_id'].nunique()
    
    print('==================================================')
    print('🏢 VISÃO GERAL: ECOSSISTEMA VENDEDORES DA BAHIA')
    print('==================================================')
    print(f'💰 Faturamento Bruto Acumulado : R$ {faturamento_total:,.2f}')
    print(f'📦 Volume de Pedidos Únicos     : {total_pedidos}')
    print(f'🎟️ Ticket Médio por Compra       : R$ {ticket_medio:,.2f}')
    
    # ==================================================
    # Quebra de Performance por Rota Logística
    # ==================================================
    print('\n==================================================')
    print('🚚 PERFORMANCE POR ROTA LOGÍSTICA')
    print('==================================================')
    
    rotas = df.groupby('rota_logistica').agg(
        faturamento=('price', 'sum'),
        qtd_itens=('product_id', 'count'),
        prazo_medio_real=('dias_entrega_real', 'mean'),
        prazo_medio_estimado=('dias_prazo_estimado', 'mean'),
        nota_media_cliente=('review_score', 'mean')
    ).reset_index()

    for r in rotas.itertuples():
        df_rota = df[df['rota_logistica'] == r.rota_logistica]
        df_entregue = df_rota[df_rota['status_prazo'] != 'Não Entregue']
        
        total_entregue = len(df_entregue)
        total_atrasado = len(df_entregue[df_entregue['status_prazo'] == 'Atrasado'])
        taxa_atraso = (total_atrasado / total_entregue * 100) if total_entregue > 0 else 0

        print(f'\n📍 ROTA: {r.rota_logistica.upper()}')
        print(f'   ↳ Faturamento na Rota : R$ {r.faturamento:,.2f} ({r.qtd_itens} itens)')
        print(f'   ↳ Lead Time Real Médio: {r.prazo_medio_real:.1f} dias (Promessa: {r.prazo_medio_estimado:.1f} dias)')
        print(f'   ↳ Índice de Atraso    : {taxa_atraso:.2f}%')
        print(f'   ↳ Satisfação (Review) : {r.nota_media_cliente:.2f} / 5.0')

    # ==================================================
    # ✨ NOVO BLOCO: Polos Produtores / Cidades Vendedoras
    # ==================================================
    print('\n==================================================')
    print('🏭 RANKING DOS POLOS VENDEDORES DA BAHIA')
    print('==================================================')
    
    # Agrupamos por cidade do vendedor para entender de onde sai a mercadoria
    polos_vendedores = df.groupby('seller_city').agg(
        faturamento_polo=('price', 'sum'),
        itens_despachados=('product_id', 'count'),
        vendedores_ativos=('seller_id', 'nunique'),
        ticket_medio_polo=('price', 'mean')
    ).sort_values(by='faturamento_polo', ascending=False).reset_index()

    for i, polo in enumerate(polos_vendedores.itertuples(), 1):
        print(f'   {i}º {polo.seller_city:<20} ↳ Fat: R$ {polo.faturamento_polo:,.2f} | Sellers: {polo.vendedores_ativos} | Qtd Itens: {polo.itens_despachados}')

    # ==================================================
    # Diagnóstico Crítico: Top 5 Categorias e Cidades Foco
    # ==================================================
    print('\n==================================================')
    print('🎯 TOP 5 CATEGORIAS DE MAIOR FATURAMENTO (BA)')
    print('==================================================')
    top_cats = df.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(5)
    for i, (cat, fat) in enumerate(top_cats.items(), 1):
        print(f'   {i}º {cat:<25} ↳ Faturamento: R$ {fat:,.2f}')

    print('\n==================================================')
    print('🏙️ TOP 5 CIDADES DESTINO QUE MAIS COMPRAM DA BA')
    print('==================================================')
    top_cidades = df.groupby(['customer_city', 'customer_state']).size().sort_values(ascending=False).head(5)
    for i, ((cidade, uf), qtd) in enumerate(top_cidades.items(), 1):
        print(f'   {i}º {cidade} ({uf}) ↳ {qtd} pedidos entregues')
    print('==================================================\n')

if __name__ == '__main__':
    executar_diagnostico_avancado()
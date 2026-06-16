  # OlistBA-Analytics

OlistBA: Data Engineering & Analytics Pipeline  

Este repositório documenta o desenvolvimento de uma arquitetura de processamento 
de dados ponta a ponta, utilizando o Dataset público da Olist (Kaggle). O objetivo 
central foi a criação de um pipeline de ETL (Extract, Transform, Load) e uma camada de 
Analytics para diagnosticar o desempenho comercial do estado da Bahia no e
commerce nacional, abrangendo o período de Setembro de 2016 a Outubro de 2018. 

# A Oportunidade: O Cenário Baiano, Análise Macro e Microeconômica Regional. 

POSIÇÃO DA BAHIA NO CENÁRIO NACIONAL (MARKET SHARE)  

A análise dos dados em nível nacional revela um importante retrato sobre a força 
econômica do estado no ecossistema digital, evidenciando um cenário de Balança 
Comercial Digital Deficitária:   

• Participação de Consumo (Compra): A Bahia responde por 3,76% do volume 
financeiro movimentado no e-commerce nacional, totalizando R$ 511 mil em compras 
capturadas na plataforma.   

• Participação de Produção (Venda): Como polo produtor, os lojistas do estado 
respondem por 2,09% do market share nacional, gerando um faturamento bruto 
acumulado de R$ 294  mil.   

# • Diagnóstico Estratégico: Existe uma demanda de consumo interna na Bahia que 
supera a capacidade ou o sortimento de oferta dos vendedores locais atuais. O capital 
digital do estado "vaza" para outras regiões produtores (como o Sudeste), gerando uma 
clara oportunidade para a atração e desenvolvimento de novos sellers regionais.   

# Engenharia de Analytics: Processamento de Market Share e Assimetria de Tickets 
Médios  

Para traduzir o comportamento de consumo e venda da região, desenvolvi um motor 
de processamento no módulo de Analytics. O algoritmo unifica tabelas nacionais e isola 
o comportamento da Bahia em duas frentes de faturamento (seller_state vs. 
customer_state), calculando os desvios e os tickets médios reais por pedido para 
mapear a viabilidade econômica de investimentos locais  

# 2. O PARADOXO DOS TICKETS MÉDIOS   

O indicador de Ticket Médio expõe duas dinâmicas operacionais completamente 
distintas quando contrastamos o comportamento de venda e de compra do estado:   

• Ticket Médio de Venda (BA Fornecedora): R$ 516,70 por compra.   
Este valor é considerado extremamente alto para os padrões do ecommerce brasileiro 
(R$ 119,98) de varejo massivo. Ele indica uma operação concentrada no modelo de 
distribuição ou comércio de bens duráveis de alto valor agregado.   

• Ticket Médio de Compra (BA Consumidora): R$ 152,28 por compra.  
Representa o comportamento clássico do consumidor final físico (B2C): compras 
pulverizadas, de menor valor unitário, focadas em reposição de itens cotidianos e uso 
pessoal. 

Saldo Comercial: O estado apresenta um déficit comercial digital de R$ 217,3 mil, 

reforçando a oportunidade estratégica para o desenvolvimento de novos sellers 
regionais e a retenção de capital dentro do estado. 

# Engenharia de Pipelines: Arquitetura Decoupled para Analytics (gerar vs. 
analisar)  

Para viabilizar este diagnóstico sem sobrecarregar a memória do ambiente ou 
gerar acoplamento rígido de código, a arquitetura do módulo foi desenhada em 
duas etapas independentes de processamento, simulando práticas reais de Data 
Lakehouse:  

 1. gerar_base_dash.py (Camada de Transformação/Ingestão):

Consolida as tabelas nacionais originais (olist_order_items_dataset, 
olist_orders_dataset, etc.), executa os tratamentos de nulos, formatações 
de data (datetime) e exporta uma base unificada, limpa e indexada 
focada estritamente no ecossistema da Bahia.  

 2. analisar_base_dash.py (Camada de Business Intelligence/Agrupamento): 

Consome diretamente a base higienizada gerada na etapa anterior e 
executa os cálculos matemáticos avançados (como o agregador duplo de 
agregação de carrinho e média de faturamento) para servir os KPIs finais 
com alta performance de tempo de execução.  

# Arquitetura de Processamento e Ferramentas 

O projeto foi estruturado em uma arquitetura de camadas, onde cada tecnologia 
atua em um estágio específico da cadeia de valor do dado: 

 • Camada de Armazenamento (SQL): 
O MySQL foi utilizado como o repositório central dos dados brutos. Ele preserva a integridade original do dataset e serve 
como base para consultas exploratórias iniciais e auditorias de consistência. 

 • Camada de Processamento (Python): 
Utilizei Python para o tratamento e limpeza (Data Cleaning) dos dados. Através de scripts automatizados, 
transformei a base bruta em DataFrames limpos e otimizados, prontos para 
consumo. 

 • Camada de Visualização (Power BI): 
Os DataFrames tratados foram exportados e carregados no Power BI. Esta abordagem simplificou drasticamente a 
modelagem no ambiente de BI, permitindo focar exclusivamente na criação de 
medidas (DAX) complexas e na construção de dashboards focados em KPIs de 
negócio. 

# Conclusão e Próximos Passos 

A análise demonstra um claro potencial de expansão para sellers baianos, capaz de 
movimentar o mercado interno, especialmente através da oferta de produtos com 
melhor relação custo-benefício em termos de frete e valor de ticket. A estratégia de 
incentivo a novos lojistas locais é fundamental para potencializar o mercado, reduzir 
a dependência externa e promover a fixação de renda dentro do estado. 
Como próximos passos, pretendo aprofundar esta análise com técnicas de Machine 
Learning para prever padrões de demanda futura e identificar as categorias de 
produtos com maior aderência e viabilidade logística para o consumidor baiano.
a dependência externa e promover a fixação de renda dentro do estado. 
Como próximos passos, pretendo aprofundar esta análise com técnicas de Machine 
Learning para prever padrões de demanda futura e identificar as categorias de 
produtos com maior aderência e viabilidade logística para o consumidor baiano. 

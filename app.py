# Imports
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from gower import gower_matrix
from scipy.spatial.distance import pdist, squareform

# Set no tema do seaborn para melhorar o visual dos plots
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

#funcao para o filtro

def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)
    
# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def main():
   # Configuração inicial da página da aplicação
   st.set_page_config(page_title='Oline shoppers purchase intention',
                      layout="wide",
                      initial_sidebar_state='expanded')

   # Título principal da aplicação
   st.write('## Atenção:')
   st.write('Dependendo do tamanho da base, os graficos podem demorar aproximadamente 60 minutos para serem gerados.')
   
   st.write("""# O que a apliçação vai tratar:

   A base trata de registros de 12.330 sessões de acesso a páginas, cada sessão sendo de um único usuário em um período de 12 meses, para posteriormente estudarmos a relação entre o design da página e o perfil do cliente - 
    "Será que clientes com comportamento de navegação diferentes possuem propensão a compra diferente?"
    Nosso objetivo agora é agrupar as sessões de acesso ao portal considerando o comportamento de acesso e informações da data, como a proximidade a uma data especial, fim de semana e o mês.
   """)
   st.write("""
    |Variavel                |Descrição          | 
|------------------------|:-------------------| 
|Administrative          | Quantidade de acessos em páginas administrativas| 
|Administrative_Duration | Tempo de acesso em páginas administrativas | 
|Informational           | Quantidade de acessos em páginas informativas  | 
|Informational_Duration  | Tempo de acesso em páginas informativas  | 
|ProductRelated          | Quantidade de acessos em páginas de produtos | 
|ProductRelated_Duration | Tempo de acesso em páginas de produtos | 
|BounceRates             | *Percentual de visitantes que entram no site e saem sem acionar outros *requests* durante a sessão  | 
|ExitRates               | * Soma de vezes que a página é visualizada por último em uma sessão dividido pelo total de visualizações | 
|PageValues              | * Representa o valor médio de uma página da Web que um usuário visitou antes de concluir uma transação de comércio eletrônico | 
|SpecialDay              | Indica a proximidade a uma data festiva (dia das mães etc) | 
|Month                   | Mês  | 
|OperatingSystems        | Sistema operacional do visitante | 
|Browser                 | Browser do visitante | 
|Region                  | Região | 
|TrafficType             | Tipo de tráfego                  | 
|VisitorType             | Tipo de visitante: novo ou recorrente | 
|Weekend                 | Indica final de semana | 
|Revenue                 | Indica se houve compra ou não |

\* variávels calculadas pelo google analytics
""")

   st.markdown("---")

   # Botão para carregar arquivo na aplicação
   st.sidebar.write("## Suba o arquivo")
   data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

   # Verifica se há conteúdo carregado na aplicação
   if data_file_1 is not None:
       df = pd.read_csv(data_file_1)

       st.write('## Análise descritiva')
       st.write('Verificação da distribuição das variáveis, tratamento de dados missing caso existam')

       variaveis = ['Administrative', 'Administrative_Duration', 'Informational',
       'Informational_Duration', 'ProductRelated', 'ProductRelated_Duration','SpecialDay','Month']
       variaveis_cat = ['Month']
       df1 = pd.get_dummies(df[variaveis].dropna())
       st.write(df1.head())

       vars_cat = [True if x in {'Month_Aug', 'Month_Dec','Month_Feb','Month_Jul','Month_June','Month_Mar','Month_May','Month_Nov','Month_Oct','Month_Sep'} else False for x in df1.columns]

       st.write('## Variáveis de agrupamento')
       st.write('Selecione as variáveis desejadas no filtro na parte esquerda da tela.')
       with st.sidebar.form(key='my_form'):
           
           st.write('VARIAVEIS DISPONIVEIS:', variaveis)
           variaveis.append('all')
           variaveis_selected =  st.multiselect("Variaveis", variaveis, ['all'])
           st.write('VARIAVEIS SELECIONADAS:', variaveis_selected)

           df1 = multiselect_filter(df1, 'variaveis', variaveis_selected)
           
           submit_button = st.form_submit_button(label='Aplicar')

       st.write('## Número de Grupos')
       st.write('Nesta atividade vamos adotar uma abordagem bem pragmática e avaliar agrupamentos hierárquicos com 3 e 4 grupos, por estarem bem alinhados com uma expectativa e estratégia do diretor da empresa.')
       
       st.write('## Análise com 3 grupos')

       distancia_gower = gower_matrix(df1, cat_features=vars_cat)
       gdv = squareform(distancia_gower,force='tovector')
       Z = linkage(gdv, method='complete')
       Z_df = pd.DataFrame(Z,columns=['id1','id2','dist','n'])
       df1['grupo'] = fcluster(Z, 3, criterion='maxclust')
       df1.grupo.value_counts()
       df2 = df.reset_index().merge(df1.reset_index(), how='left')
       st.write(df2.groupby(['Month','grupo','Revenue'])['index'].count().unstack().fillna(0).style.format(precision=0))

       st.write('## Análise com 4 grupos')
       df1['grupo1'] = fcluster(Z, 4, criterion='maxclust')
       df1.grupo.value_counts()
       df2 = df.reset_index().merge(df1.reset_index(), how='left')
       st.write(df2.groupby(['Month','grupo1','Revenue'])['index'].count().unstack().fillna(0).style.format(precision=0))

       st.write('## Avaliação com 3 grupos')
       fig = sns.catplot(data=df2, x="Month", y="Revenue", hue="grupo", kind="swarm")
       st.pyplot(fig)

       st.write('## Avaliação com 4 grupos')
       fig1 = sns.catplot(data=df2, x="Month", y="Revenue", hue="grupo1", kind="swarm")
       st.pyplot(fig1)


       st.write('## Avaliação dos resultados')
       st.write('Dependendo da base de dados que utilizar os resultados podem ser variados. Os gráficos gerados para análise estão dividos em grupos definidos pelos clusters, e a variavel alvo é se teve compra ou não.')
       st.write('No eixo y=0, são os clientes que não converteram em compras, já no eixo y=1, representa os clientes que converteram em compras.')
       st.write('Boa análise')


       

if __name__ == '__main__':
   main()
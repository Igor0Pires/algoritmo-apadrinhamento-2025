import pandas as pd
import numpy as np
from collections import Counter
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpStatus


def filtro_colunas(df, indices):
    """
    Filtra as colunas de um DataFrame com base em uma lista de índices.

    Args:
        df (pd.DataFrame): O DataFrame original.
        indices (list): Lista de índices das colunas a serem filtradas.

    Returns:
        pd.DataFrame: DataFrame com as colunas filtradas.
    """
    df = df.drop_duplicates(subset=df.columns[indices[0]], keep='last')
    return df.iloc[:, indices]


def extrair_valores_unicos_ordenados(df, num=None):
    """
    Extrai valores únicos e ordenados das colunas de um DataFrame.

    Args:
        df (pd.DataFrame): O DataFrame original.
        num (int, optional): Número de colunas a serem consideradas. Se None, todas as colunas são usadas.

    Returns:
        tuple: Uma lista de valores únicos e uma lista de índices de início de novas colunas.
    """
    contador = Counter()
    coluna_indices = {}

    if num is None:
        num = len(df.columns)

    # Itera sobre as colunas e células do DataFrame
    for col_index, col in enumerate(df.columns[1:num], start=1):
        for cell in df[col]:
            # Divide a célula em valores separados por vírgula
            values = [value.strip() for value in cell.split(',')]
            # Atualiza o contador com os valores
            contador.update(values)
            # Mapeia os valores para as colunas originais
            for value in values:
                if value not in coluna_indices:
                    coluna_indices[value] = col_index

    # Filtra valores únicos que aparecem mais de uma vez
    lista_unica = [value for value, count in contador.items() if count > 1]
    if '' in lista_unica:
        lista_unica.remove('')

    # Identifica os índices de início de novas colunas
    indices_novas_colunas = []
    for i, item in enumerate(lista_unica):
        if i == 0 or coluna_indices[item] != coluna_indices[lista_unica[i - 1]]:
            indices_novas_colunas.append(i + 1)
    lista_unica.insert(0, 'Nome')

    return lista_unica, indices_novas_colunas


def gerar_matriz_interesse(df, df_dummy, lista_indices, incluir_ultima_coluna=False):
    """
    Gera uma matriz de interesse com base nos dados do DataFrame.

    Args:
        df (pd.DataFrame): O DataFrame original.
        df_dummy (pd.DataFrame): DataFrame vazio para armazenar a matriz de interesse.
        lista_indices (list): Lista de índices de início de novas colunas.
        incluir_ultima_coluna (bool, optional): Se True, inclui a última coluna do DataFrame original.

    Returns:
        pd.DataFrame: DataFrame preenchido com a matriz de interesse.
    """
    for individuo in df.itertuples(index=False):
        dummy = [individuo[0]]  # Nome do indivíduo

        # Mapeia os interesses para valores binários (1 se presente, 0 se ausente)
        interesses = [individuo[indice] for indice in range(1, len(individuo) - int(incluir_ultima_coluna))]
        dummy.extend([
            int(col in interesses[i])  # 1 se presente, 0 se ausente
            for i, start in enumerate(lista_indices)  # Índices de início de novas colunas
            for col in df_dummy.columns[start:start + (lista_indices[i + 1] - start if i + 1 < len(lista_indices) else len(df_dummy.columns) - start)]  # Colunas de interesse
        ])

        if incluir_ultima_coluna:
            # Adiciona o número de afilhados (última coluna)
            dummy.pop()
            dummy.append(individuo[-1])

        # Adiciona a linha ao DataFrame
        df_dummy.loc[len(df_dummy)] = dummy

    return df_dummy

def algoritmo_apadrinhamento_lp(df_afilhados_dummy, df_padrinhos_dummy):
    """
    Realiza o match entre afilhados e padrinhos usando otimização linear.

    Args:
        df_afilhados_dummy (pd.DataFrame): DataFrame de afilhados.
        df_padrinhos_dummy (pd.DataFrame): DataFrame de padrinhos.

    Returns:
        pd.DataFrame: DataFrame com os matches (Nome afilhado, Compatibilidade, Nome padrinho).
    """
    # Filtra colunas comuns entre afilhados e padrinhos
    colunas_comuns = df_padrinhos_dummy.columns.intersection(df_afilhados_dummy.columns).tolist()
    colunas_comuns.append('Numero de afilhados')  # Adiciona a coluna de limite de afilhados
    df_padrinhos_dummy = df_padrinhos_dummy[colunas_comuns]
    df_afilhados_dummy = df_afilhados_dummy[colunas_comuns[:-1]]  # Remove a última coluna para afilhados

    # Cria a matriz de custo (diferença entre características)
    num_afilhados = len(df_afilhados_dummy)
    num_padrinhos = len(df_padrinhos_dummy)
    cost_matrix = np.zeros((num_afilhados, num_padrinhos))

    for i, afilhado in df_afilhados_dummy.iterrows():
        for j, padrinho in df_padrinhos_dummy.iterrows():
            cost_matrix[i, j] = sum(afilhado.iloc[1:] != padrinho.iloc[1:-1])  # Número de características diferentes

    # Cria o problema de otimização
    prob = LpProblem("Matching_Optimization", LpMinimize)

    # Variáveis binárias: x[i][j] = 1 se o afilhado i for atribuído ao padrinho j
    x = [[LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(num_padrinhos)] for i in range(num_afilhados)]

    # Função objetivo: minimizar a soma das diferenças
    prob += lpSum(cost_matrix[i][j] * x[i][j] for i in range(num_afilhados) for j in range(num_padrinhos))

    # Restrições
    for i in range(num_afilhados):
        prob += lpSum(x[i][j] for j in range(num_padrinhos)) == 1  # Cada afilhado deve ser atribuído a um padrinho

    for j in range(num_padrinhos):
        prob += lpSum(x[i][j] for i in range(num_afilhados)) <= df_padrinhos_dummy.loc[j, 'Numero de afilhados']  # Limite de afilhados por padrinho

    # Resolve o problema
    prob.solve()

    # Cria o DataFrame final com os matches
    df_final = pd.DataFrame(columns=['Nome afilhado', 'Compatibilidade', 'Nome padrinho'])
    for i in range(num_afilhados):
        for j in range(num_padrinhos):
            if x[i][j].varValue == 1:  # Se a variável binária for 1, o afilhado foi atribuído ao padrinho
                nome_afilhado = df_afilhados_dummy.iloc[i]['Nome']
                nome_padrinho = df_padrinhos_dummy.iloc[j]['Nome']
                porcentagem_match = round((1 - (cost_matrix[i, j] / len(df_afilhados_dummy.columns[1:]))) * 100, 2)
                df_final.loc[len(df_final)] = [nome_afilhado, porcentagem_match, nome_padrinho]
    print(LpStatus[prob.status])

    return df_final


def fazer_match_na_hora(afilhado, df_padrinhos):
    """
    Encontra o padrinho mais compatível para um afilhado específico em tempo real.

    Args:
        afilhado (pd.Series): Dados do afilhado (uma linha de um DataFrame).
        df_padrinhos (pd.DataFrame): DataFrame de padrinhos.

    Returns:
        tuple: Nome do padrinho mais compatível e a porcentagem de compatibilidade.
    """
    # Extrai valores únicos e gera a matriz de interesse para os padrinhos
    lista_unica_padrinhos, indices_padrinhos = extrair_valores_unicos_ordenados(df_padrinhos, -1)
    df_padrinhos_dummy = pd.DataFrame(columns=lista_unica_padrinhos + ['Numero de afilhados'])
    gerar_matriz_interesse(df_padrinhos, df_padrinhos_dummy, indices_padrinhos, incluir_ultima_coluna=True)

    # Gera a matriz de interesse para o afilhado
    df_afilhado_dummy = pd.DataFrame(columns=lista_unica_padrinhos)
    gerar_matriz_interesse(pd.DataFrame([afilhado]), df_afilhado_dummy, indices_padrinhos)

    # Garante que as colunas estejam alinhadas
    df_afilhado_dummy = df_afilhado_dummy[df_padrinhos_dummy.columns[:-1]]  # Remove a coluna 'Numero de afilhados'

    # Calcula a compatibilidade entre o afilhado e cada padrinho
    compatibilidades = []
    for _, padrinho in df_padrinhos_dummy.iterrows():
        compatibilidade = sum(df_afilhado_dummy.iloc[0] == padrinho.iloc[:-1])  # Compara colunas alinhadas
        compatibilidades.append(compatibilidade)

    # Encontra o padrinho com a maior compatibilidade
    index = np.argmax(compatibilidades)
    padrinho_escolhido = df_padrinhos_dummy.iloc[index]['Nome']
    porcentagem_compatibilidade = round((compatibilidades[index] / len(df_afilhado_dummy.columns)) * 100, 2)

    return padrinho_escolhido, porcentagem_compatibilidade

def algoritmo_apadrinhamento_2024(df_afilhados_dummy, df_padrinhos_dummy):
    """
    Realiza o match entre afilhados e padrinhos usando uma métrica de distância.

    Args:
        df_afilhados_dummy (pd.DataFrame): DataFrame de afilhados.
        df_padrinhos_dummy (pd.DataFrame): DataFrame de padrinhos.

    Returns:
        pd.DataFrame: DataFrame com os matches (Nome bixo, Compatibilidade, Nome padrinho, Distância).
    """
    # Filtra colunas comuns entre afilhados e padrinhos
    colunas_comuns = df_padrinhos_dummy.columns.intersection(df_afilhados_dummy.columns).tolist()
    colunas_comuns.append('Numero de afilhados')  # Adiciona a coluna de limite de afilhados
    df_padrinhos_dummy_cruzados = df_padrinhos_dummy[colunas_comuns]
    df_afilhados_dummy_cruzados = df_afilhados_dummy[colunas_comuns[:-1]]  # Remove a última coluna para afilhados

    # DataFrame final para armazenar os resultados
    df_final = pd.DataFrame(columns=['Nome bixo', 'Compatibilidade', 'Nome padrinho', 'Distância'])
    padrinhos_afilhados_count = {padrinho['Nome']: 0 for _, padrinho in df_padrinhos_dummy_cruzados.iterrows()}

    # Itera sobre cada afilhado
    for bixo in df_afilhados_dummy_cruzados.itertuples():
        distancias_padrinhos = {}

        # Calcula a distância para cada padrinho disponível
        for padrinho in df_padrinhos_dummy_cruzados.itertuples():
            if padrinhos_afilhados_count[padrinho.Nome] < padrinho[-1]:  # Verifica o limite de afilhados
                distancia_atual = sum(
                    (int(getattr(bixo, col.replace(' ', '_').replace('/', '_'), 0)) - int(getattr(padrinho, col.replace(' ', '_').replace('/', '_'), 0))) ** 2
                    for col in df_afilhados_dummy_cruzados.columns[1:]  # Ignora 'Nome'
                )
                distancias_padrinhos[distancia_atual] = padrinho

        # Encontra o padrinho com a menor distância
        if distancias_padrinhos:
            melhor_distancia = min(distancias_padrinhos.keys())
            melhor_padrinho = distancias_padrinhos[melhor_distancia]
            porcentagem_match = round((1 - (melhor_distancia / len(df_afilhados_dummy_cruzados.columns[1:]))) * 100, 2)
            df_final.loc[len(df_final)] = [bixo.Nome, porcentagem_match, melhor_padrinho.Nome, melhor_distancia]
            padrinhos_afilhados_count[melhor_padrinho.Nome] += 1

    return df_final
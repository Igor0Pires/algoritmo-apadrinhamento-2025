import streamlit as st
import pandas as pd
from main import (
    filtro_colunas,
    extrair_valores_unicos_ordenados,
    gerar_matriz_interesse,
    algoritmo_apadrinhamento_lp,
    fazer_match_na_hora
)

# Configuração da página
st.set_page_config(page_title="Sistema de Apadrinhamento", layout="wide")

# Título do aplicativo
st.title("Sistema de Apadrinhamento")

# Inicializa o DataFrame de matches na sessão, se não existir
if 'df_final' not in st.session_state:
    st.session_state.df_final = pd.DataFrame(columns=['Nome afilhado', 'Compatibilidade', 'Nome padrinho'])

# Upload de arquivos
st.header("Upload de Arquivos")
uploaded_file_afilhados = st.file_uploader("Faça upload do arquivo CSV de afilhados", type=["csv"])
uploaded_file_padrinhos = st.file_uploader("Faça upload do arquivo CSV de padrinhos", type=["csv"])

# Carregar dados
if uploaded_file_afilhados is not None and uploaded_file_padrinhos is not None:
    try:
        # Lê os arquivos CSV
        if "df_padrinhos" not in st.session_state:
            df_padrinhos = pd.read_csv(uploaded_file_padrinhos)
            st.session_state.df_padrinhos = df_padrinhos
        if "df_afilhados" not in st.session_state:
            df_afilhados = pd.read_csv(uploaded_file_afilhados)
            st.session_state.df_afilhados = df_afilhados
        
        with st.expander("Ver DataFrames Carregados"):
            st.subheader("DataFrame de Afilhados")
            st.dataframe(df_afilhados)
            st.subheader("DataFrame de Padrinhos")
            st.dataframe(df_padrinhos)

        # Multi seleção para escolher as colunas relevantes
        st.subheader("Selecione as colunas relevantes para os afilhados (Nome completo deve ser a primeira coluna)")
        colunas_afilhados = df_afilhados.columns.tolist()
        colunas_afilhados_selecionadas = st.multiselect("Colunas disponíveis:", colunas_afilhados, default=colunas_afilhados[1:])

        st.subheader("Selecione as colunas relevantes para os padrinhos (Nome completo deve ser a primeira coluna e Número de afilhados deve ser a última coluna)")
        colunas_padrinhos = df_padrinhos.columns.tolist()
        colunas_padrinhos_selecionadas = st.multiselect("Colunas disponíveis:", colunas_padrinhos, default=colunas_padrinhos[1:])

        # Lista as colunas selecionadas como indices
        indices_afilhados = [colunas_afilhados.index(col) for col in colunas_afilhados_selecionadas]
        indices_padrinhos = [colunas_padrinhos.index(col) for col in colunas_padrinhos_selecionadas]

        # Filtra as colunas relevantes
        df_afilhados = filtro_colunas(df_afilhados, indices_afilhados)
        df_padrinhos = filtro_colunas(df_padrinhos, indices_padrinhos)
        

        # Transforma todas as células em string
        df_afilhados = df_afilhados.map(str)
        df_padrinhos.iloc[:, :-1] = df_padrinhos.iloc[:, :-1].map(str)

            # Renomeia a primeira coluna para 'Nome completo'
        df_afilhados.rename(columns={df_afilhados.columns[0]: 'Nome completo'}, inplace=True)
        df_padrinhos.rename(columns={df_padrinhos.columns[0]: 'Nome completo'}, inplace=True)
        
        # Renomeia a última coluna para 'Numero de afilhados'
        df_padrinhos.rename(columns={df_padrinhos.columns[-1]: 'Numero de afilhados'}, inplace=True)
        # Armazena os DataFrames na sessão
        st.session_state.df_afilhados = df_afilhados
        st.session_state.df_padrinhos = df_padrinhos
    except Exception as e:
        pass

    try:
        st.header("Alterar Número de Afilhados Aceitos pelo Padrinho")
        padrinho_selecionado = st.selectbox(
            "Selecione um padrinho:",
            st.session_state.df_padrinhos['Nome completo']
        )
        
        novo_limite = st.number_input(
            f"Novo número de afilhados aceitos para {padrinho_selecionado}:",
            min_value=0,
            value=int(st.session_state.df_padrinhos.loc[
                st.session_state.df_padrinhos['Nome completo'] == padrinho_selecionado, 'Numero de afilhados'
            ].values[0])
        )
        if st.button("Atualizar Limite"):
            st.session_state.df_padrinhos.loc[
                st.session_state.df_padrinhos['Nome completo'] == padrinho_selecionado, 'Numero de afilhados'
            ] = novo_limite
            st.success(f"Limite de afilhados para {padrinho_selecionado} atualizado para {novo_limite}!")
    except Exception as e:
        st.error(f"Erro ao filtrar colunas. Por favor, verifique se filtros foram aplicados corretamente. Erro: {e}")
    numero_afilhados = st.session_state.df_afilhados.shape[0]
    numero_afilhados_aceitos = st.session_state.df_padrinhos['Numero de afilhados'].sum()

    if numero_afilhados > numero_afilhados_aceitos:
        st.warning(f"**Atenção!** O número de afilhados ({numero_afilhados}) é maior que o número total de afilhados aceitos pelos padrinhos ({numero_afilhados_aceitos}). Para garantir que todos os afilhados sejam atendidos, considere aumentar o número de afilhados aceitos por padrinho.")

    with st.expander("Ver DataFrames Carregados"):
            st.subheader("DataFrame de Padrinhos")
            st.dataframe(st.session_state.df_padrinhos)

# Fazer match batch
if 'df_afilhados' in st.session_state and 'df_padrinhos' in st.session_state:
    st.header("Realizar Match (Batch)")
    if st.button("Fazer Match Batch"):

        df_afilhados = st.session_state.df_afilhados
        df_padrinhos = st.session_state.df_padrinhos

        # Extrai valores únicos e gera matrizes de interesse
        lista_unica_afilhados, indices_afilhados = extrair_valores_unicos_ordenados(df_afilhados)
        lista_unica_padrinhos, indices_padrinhos = extrair_valores_unicos_ordenados(df_padrinhos, -1)

        df_afilhados_dummy = pd.DataFrame(columns=lista_unica_afilhados)
        df_padrinhos_dummy = pd.DataFrame(columns=lista_unica_padrinhos + ['Numero de afilhados'])

        gerar_matriz_interesse(df_afilhados, df_afilhados_dummy, indices_afilhados)
        gerar_matriz_interesse(df_padrinhos, df_padrinhos_dummy, indices_padrinhos, incluir_ultima_coluna=True)

        # Realiza o match usando o algoritmo de otimização linear
        df_final_batch = algoritmo_apadrinhamento_lp(df_afilhados_dummy, df_padrinhos_dummy)

        # Adiciona os resultados ao DataFrame de matches
        st.session_state.df_final = pd.concat([st.session_state.df_final, df_final_batch], ignore_index=True)
        st.success("Match batch concluído!")

        # Exibe os resultados
        st.write("Resultados do Match Batch:")
        st.dataframe(df_final_batch)

# Exibir matches anteriores
if 'df_final' in st.session_state:
    st.header("Matches Anteriores")
    st.dataframe(st.session_state.df_final)
    st.download_button(
        label="Baixar Matches Anteriores",
        data=st.session_state.df_final.to_csv(index=False),
        file_name="matches.csv",
        mime="text/csv"
    )
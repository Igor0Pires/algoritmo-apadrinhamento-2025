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

if 'x' not in st.session_state:
        st.session_state.x = 0
x = st.session_state.x
# Carregar dados
if uploaded_file_afilhados is not None and uploaded_file_padrinhos is not None:
    try:
        # Lê os arquivos CSV
        df_afilhados = pd.read_csv(uploaded_file_afilhados)
        df_padrinhos = pd.read_csv(uploaded_file_padrinhos)

        # Multi seleção para escolher as colunas relevantes
        st.subheader("Selecione as colunas relevantes para os afilhados")
        colunas_afilhados = df_afilhados.columns.tolist()
        colunas_afilhados_selecionadas = st.multiselect("Colunas disponíveis:", colunas_afilhados, default=colunas_afilhados)

        st.subheader("Selecione as colunas relevantes para os padrinhos")
        colunas_padrinhos = df_padrinhos.columns.tolist()
        colunas_padrinhos_selecionadas = st.multiselect("Colunas disponíveis:", colunas_padrinhos, default=colunas_padrinhos)

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

    # Alterar número de afilhados por padrinho
    x += int(st.button("Filtrar Colunas"))
if x and 'df_padrinhos' in st.session_state:
    
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
# Fazer match batch
if 'df_afilhados' in st.session_state and 'df_padrinhos' in st.session_state:
    st.header("Realizar Match (Batch)")
    if st.button("Fazer Match Batch"):
        # Extrai valores únicos e gera matrizes de interesse
        lista_unica_afilhados, indices_afilhados = extrair_valores_unicos_ordenados(st.session_state.df_afilhados)
        lista_unica_padrinhos, indices_padrinhos = extrair_valores_unicos_ordenados(st.session_state.df_padrinhos, -1)

        df_afilhados_dummy = pd.DataFrame(columns=lista_unica_afilhados)
        df_padrinhos_dummy = pd.DataFrame(columns=lista_unica_padrinhos + ['Numero de afilhados'])

        gerar_matriz_interesse(st.session_state.df_afilhados, df_afilhados_dummy, indices_afilhados)
        gerar_matriz_interesse(st.session_state.df_padrinhos, df_padrinhos_dummy, indices_padrinhos, incluir_ultima_coluna=True)

        # Realiza o match usando o algoritmo de otimização linear
        df_final_batch = algoritmo_apadrinhamento_lp(df_afilhados_dummy, df_padrinhos_dummy)

        # Adiciona os resultados ao DataFrame de matches
        st.session_state.df_final = pd.concat([st.session_state.df_final, df_final_batch], ignore_index=True)
        st.success("Match batch concluído!")

        # Exibe os resultados
        st.write("Resultados do Match Batch:")
        st.dataframe(df_final_batch)

# Cadastrar afilhado manualmente
st.header("Cadastrar Afilhado Manualmente")
nome_completo = st.text_input("Nome completo")
hobbies = st.multiselect(
    "Há algum hobbie que você pratica no final de semana/tempo livre?",
    ['Anime', 'Desenho/Pintura', 'Filmes/Séries', 'Leitura', 'Música (escutar/tocar)', 'Cozinhar', 'Esporte', 'Jogo on/offline', 'Dança', 'Academia']
)
generos_filme_serie_livro = st.multiselect(
    "Quais gêneros de filme/série/livro mais gosta?",
    ['Aventura', 'Comédia', 'Drama', 'Fantasia', 'Romance', 'Ação', 'Ficção Científica', 'Suspense', 'Terror', 'Musical', 'Dorama']
)
estilo_musical = st.multiselect(
    "Qual o seu estilo musical favorito?",
    ['Funk', 'Pop', 'Rap', 'Sertanejo', 'Mpb', 'Rock', 'Eletrônica', 'Indie', 'Kpop', 'Pagode', 'Trap', 'Forró', 'Samba', 'Jazz', 'R&B', 'Alternativa', 'Reggae', 'Clássica', 'Axé']
)
animal_estimacao = st.selectbox(
    "Você tem animal de estimação?",
    ['Cachorro', 'Gato', 'Não tenho', 'Peixe', 'Tartaruga', 'Passarinho']
)
esportes = st.multiselect(
    "Você pratica algum esporte?",
    ['Vôlei', 'Futebol', 'Natação', 'Não pratico nenhum esporte', 'Artes Marciais', 'Atletismo', 'Basquete', 'E-Sports', 'Handebol', 'Tênis', 'Rugby', 'Patinação']
)
tipos_role = st.multiselect(
    "Quais tipos de rolê você curte?",
    ['Cinema', 'Festa Universitária', 'Museu', 'Parque/praça', 'Praia', 'Restaurante/café', 'Rolê caseiro', 'Bar', 'Rolê Online', 'Shopping']
)

if st.button("Adicionar Afilhado Manualmente"):
    # Cria um dicionário com os dados do afilhado
    afilhado = {
        "Nome": nome_completo,
        "Hobbies": ", ".join(hobbies),
        "Gêneros Filme/Série/Livro": ", ".join(generos_filme_serie_livro),
        "Estilo Musical": ", ".join(estilo_musical),
        "Animal de Estimação": animal_estimacao,
        "Esportes": ", ".join(esportes),
        "Tipos de Rolê": ", ".join(tipos_role)
    }

    # Converte o dicionário em um DataFrame
    df_afilhado_manual = pd.DataFrame([afilhado])

    # Realiza o match em tempo real
    if 'df_padrinhos' in st.session_state:
        padrinho, compatibilidade = fazer_match_na_hora(df_afilhado_manual.iloc[0], st.session_state.df_padrinhos)
        st.success(f"Padrinho mais compatível: **{padrinho}** (Compatibilidade: **{compatibilidade}%**)")

        # Adiciona o match ao DataFrame de matches
        novo_match = pd.DataFrame({
            'Nome afilhado': [nome_completo],
            'Compatibilidade': [compatibilidade],
            'Nome padrinho': [padrinho]
        })
        st.session_state.df_final = pd.concat([st.session_state.df_final, novo_match], ignore_index=True)
    else:
        st.error("Por favor, faça upload dos arquivos de padrinhos primeiro.")

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
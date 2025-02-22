# Sistema de Apadrinhamento

Este repositório contém um sistema para realizar matches entre afilhados e padrinhos com base em interesses comuns. O sistema é composto por:

1. **Aplicativo Streamlit**: Integrado ao algoritmo para ações mais intuitivas.
2. **Notebook Jupyter**: Ferramenta de desenvolvimento e teste do algoritmo de matching.
3. **Módulo `main.py`**: Contém as funções principais do algoritmo, reutilizadas tanto no aplicativo quanto no notebook.



## Requisitos de Dados

### Formato dos Arquivos CSV

O sistema espera dois arquivos CSV como entrada:

1. **`afilhados.csv`**[^1]:
   - Colunas esperadas:
     - Nome completo
     - Colunas sobre os Interesses

2. **`padrinhos.csv`**[^1]:
   - Colunas esperadas:
     - Nome completo
     - Colunas sobre os Interesses
     - Número máximo de afilhados que o padrinho pode receber (coluna numérica)

    

### Exemplo de Dados

#### `afilhados.csv`
| Nome completo       | Hobbies                     | Gêneros Filme/Série/Livro | Estilo Musical | Animal de Estimação | Esportes               | Tipos de Rolê           |
|---------------------|-----------------------------|---------------------------|----------------|---------------------|------------------------|-------------------------|
| João Silva          | Filmes/Séries, Leitura      | Aventura, Comédia         | Rock, Pop      | Cachorro            | Futebol, Natação       | Cinema, Restaurante/café|
| Maria Oliveira      | Desenho/Pintura, Música     | Drama, Fantasia           | MPB, Jazz      | Gato                | Natação, Dança         | Museu, Parque/praça     |

#### `padrinhos.csv`
| Nome completo       | Hobbies                     | Gêneros Filme/Série/Livro | Estilo Musical | Animal de Estimação | Esportes               | Tipos de Rolê           | Numero de bixos |
|---------------------|-----------------------------|---------------------------|----------------|---------------------|------------------------|-------------------------|-----------------|
| Carlos Souza        | Filmes/Séries, Cozinhar     | Aventura, Ficção Científica| Rock, Eletrônica| Cachorro            | Futebol, Basquete      | Cinema, Bar             | 2               |
| Ana Pereira         | Leitura, Dança              | Romance, Drama            | Pop, Jazz      | Gato                | Dança, Yoga            | Museu, Restaurante/café | 3               |

## Funcionalidades

### 1. Aplicativo Streamlit

O aplicativo Streamlit oferece uma interface para realizar matches entre afilhados e padrinhos. Ele permite (por enquanto):

- **Upload de arquivos CSV**: Carregue os arquivos de afilhados e padrinhos.
- **Alterar limite de afilhados**: Ajuste o número máximo de afilhados que um padrinho pode receber.
- **Realizar match batch**: Execute o algoritmo de matching em lote para todos os afilhados e padrinhos.
- **Cadastrar afilhado manualmente**: Adicione um afilhado manualmente e encontre o padrinho mais compatível em tempo real.
- **Visualizar e exportar resultados**: Exiba os matches anteriores e exporte-os para um arquivo CSV.

#### Como Executar o Aplicativo

1. Navegue até a pasta `app/`:
```bash
    cd app
```

2. Intale as dependências:
```bash
    pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
    stereamlit run app.py
```

### 2. Notebook Jupyter
O notebook (`algoritmo.ipynb`) é uma ferramenta de desenvolvimento e teste do algoritmo de matching. Ele permite:

**Testar o algoritmo**: Execute o algoritmo de matching passo a passo.

**Visualizar resultados intermediários**: Analise as matrizes de interesse e os resultados do matching.

**Cadastrar afilhados manualmente**: Teste o cadastro manual de afilhados e o match em tempo real.

Como Usar o Notebook
Navegue até a pasta `notebook/`:

```bash
    cd notebook
```

Abra o notebook no Jupyter:
```bash
    jupyter notebook algoritmo.ipynb
```

### 3. Módulo main.py
O módulo `main.py` contém as funções principais do algoritmo de matching, que são reutilizadas tanto no aplicativo quanto no notebook. As principais funções são:

- `filtro_colunas`: Filtra as colunas relevantes dos DataFrames.

- `extrair_valores_unicos_ordenados`: Extrai valores únicos e ordenados das colunas de interesse.

- `gerar_matriz_interesse`: Gera a matriz de interesse para afilhados e padrinhos.

- `algoritmo_apadrinhamento_lp`: Realiza o match entre afilhados e padrinhos usando otimização linear.

- extra: `algoritmo_apadrinhamento_2024`: algoritmo de 2024 que foi utilizada como base dessa. [^2]

## Dependências

O projeto utiliza as seguintes bibliotecas:

- `streamlit`

- `pandas`

- `numpy`

- `pulp`

para instalar as depêndencias execute: ```bash pip install -r requirements.txt```

## Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.

[^1]: Será possivel filtrar esses dados no aplicativo e notebook.
[^2]: <small> Valeu Guigas ;)</small>
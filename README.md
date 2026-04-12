# Fuel-Insight-MVP

Aplicação full stack para predição de faixa de preço de combustível com API Flask, modelo embarcado e frontend em Vue.js (via CDN no HTML).

## Overview

O **Fuel-Insight-MVP** transforma variáveis econômicas e de mercado em predição de faixa de preço de combustível, com foco em apoio à decisão.  
Além da predição unitária, a solução entrega visão analítica com histórico, insights por região, ranking de risco, alertas e dashboard executivo.

## Objetivo

O objetivo do projeto é oferecer uma base prática de produto inteligente que:
- classifica cenários de preço de combustível com modelo de ML embarcado no backend;
- disponibiliza API documentada para consumo por frontend e integrações;
- suporta governança de modelo com versionamento e ativação controlada.

## Aplicabilidade

Aplicações típicas:
- planejamento comercial por região/segmento;
- monitoramento de risco de preço e priorização de ações;
- simulação de cenários (imposto, subsídio, petróleo) para análise estratégica;
- suporte a operações de distribuição, logística e varejo com visão orientada a dados.

## Nome do projeto

**Fuel-Insight-MVP**

## O que pode subir para o repositório (GitHub)

Pode enviar:
- Código-fonte (`backend/app`, `frontend`, `notebooks`)
- `requirements.txt`
- `README.md`
- `.env.example`
- arquivos de teste

Não deve enviar:
- `.env` (contém configuração local e pode conter segredo)
- `.venv/`
- caches (`__pycache__`, `.pytest_cache`, `.coverage`, `htmlcov/`)
- banco local (`*.db`) quando for dado local de ambiente

O `.gitignore` do projeto já foi configurado para proteger isso.

## Variáveis de ambiente

Arquivo de referência: `backend/.env.example`  
Arquivo local (não versionado): `backend/.env`

Principais variáveis:
- `JWT_SECRET_KEY`: chave JWT da API
- `DATABASE_URL`: conexão do banco (padrão: `sqlite:///fuel_mvp.db`)
- `HOST`: host da API (padrão: `127.0.0.1`)
- `PORT`: porta da API (padrão: `5000`)
- `FLASK_ENV`: `development` ou `production`
- `ENABLE_STARTUP_SEED`: `true/false` para seed inicial
- `INITIAL_SEED_SCENARIOS`: JSON array com cenários iniciais
- `ML_DATASET_PATH`: caminho/URL do dataset para treino e teste do modelo (padrão: RAW do GitHub)
- `ML_MODEL_OUTPUT_PATH`: caminho de saída do `.pkl` treinado (padrão: `app/ml/fuel_price_tier_model.pkl`)

Exemplo: 
```
# API
FLASK_ENV=development
HOST=127.0.0.1
PORT=5000

# Security
JWT_SECRET_KEY=troque-esta-chave-em-producao

# Database
DATABASE_URL=sqlite:///fuel_mvp.db

# Startup seed
ENABLE_STARTUP_SEED=true

# ML training/runtime
ML_DATASET_PATH=https://raw.githubusercontent.com/AngeloSouzaOliveira/API-Fuel-Insight-MVP/refs/heads/main/data/all_countries_combined.csv
ML_MODEL_OUTPUT_PATH=app/ml/fuel_price_tier_model.pkl

# Cenarios padrao iniciais (JSON array)
# Exemplo:
# SEED_SCENARIOS=[{"year":2024,"region":"Latin America","subsidy_regime":"partial","is_oil_producer":1,"crude_oil_usd_per_barrel":82.4,"tax_pct_of_pump_price":22.0,"gasoline_real_2024usd":1.15}]

```

## Setup rápido

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app\train_model.py
python -m app.main
```

Swagger:
- `http://127.0.0.1:5000/apidocs`

### Frontend

- Acesse frontend\index.html 
- Instale o live server na extesão do VScode 
- E após a isntalação clique com botão direito no arquivo index.html 
- Selecione a opção "Open with Live Server"
- E o servidor vai rodar o frontend

## Arquitetura backend (Blueprints)

A API Flask está organizada por domínio usando **Blueprints**, para manter o código modular e facilitar evolução:

- `app/blueprints/sistema.py`: saúde da API e redirecionamento inicial.
- `app/blueprints/auth.py`: cadastro e login.
- `app/blueprints/combustivel.py`: predição, lote, cenários, histórico, insights, dashboard e alertas.
- `app/blueprints/mercado.py`: comparativo de mercado externo.
- `app/blueprints/modelos.py`: versionamento e ativação de modelos (MLOps).
- `app/blueprints/__init__.py`: registro central dos blueprints.

Ponto de entrada:
- `app/main.py` inicializa extensões, banco, swagger e registra os blueprints.

## Logging (logger)

O projeto usa logger central em:
- `app/core.py` com `logging.basicConfig(...)` e `logger = logging.getLogger("fuel_api")`.

Onde os logs são aplicados:
- autenticação (registro e login),
- predição unitária e em lote,
- consultas analíticas (insights/dashboard),
- operações de MLOps (registro e ativação de modelo).

Objetivo dos logs:
- rastreabilidade de uso,
- auditoria funcional,
- apoio à análise de falhas e operação.


## Links da entrega:
- Dataset Kaggle: [LINK_KAGGLE](https://www.kaggle.com/datasets/samyakrajbayar/global-fuel-prices-100-years-19242024)`
- Dataset RAW (GitHub): [LINK_RAW](https://raw.githubusercontent.com/AngeloSouzaOliveira/API-Fuel-Insight-MVP/refs/heads/main/data/all_countries_combined.csv)
- Notebook Colab: [LINK_COLAB](https://drive.google.com/file/d/1cTtnGNh_syQ-bTcA0CQ8nh4Nthz_Hujc/view?usp=sharing)



## Métrica e critério de aceite do modelo

- Métrica principal: **acurácia** para classificação.
- Critério mínimo no teste automatizado: **threshold >= 0.70**.
- Regra operacional: se o teste ficar abaixo do threshold, o modelo não deve ser promovido/substituído.
- Arquivo do teste de aceite: `backend/test/test_model_performance.py`.
- Como ajustar: altere `threshold` no teste apenas com justificativa técnica e revalide com holdout/cross-validation.



## Limitações atuais e evolução

- O modelo depende da distribuição histórica do dataset e pode sofrer drift ao longo do tempo.
- O seed inicial é estático (mas já pode ser customizado por variável de ambiente).
- Próximos passos: monitoramento contínuo de performance, gatilhos de re-treino e observabilidade ampliada.

## Conformidade com Software Seguro

Já aplicado no projeto:
- autenticação JWT em rotas protegidas;
- validação estrita de entrada com schemas (tipos, limites e enums);
- segregação de configuração sensível por `.env` + `.env.example`;
- controle de acesso por perfil nas rotas de MLOps.

Aplicação recomendada para produção:
- anonimização/pseudonimização de campos sensíveis antes de persistência;
- rotação periódica de `JWT_SECRET_KEY` e gestão por cofre de segredos;
- trilha de auditoria centralizada e monitoramento de tentativas inválidas;
- política de menor privilégio por perfil e revisão periódica de permissões.

## API (detalhada)

### 1) `GET /api/saude`
- Objetivo: verificar se a API está online.
- Auth: não exige token.
- Parâmetros: nenhum.

### 2) `POST /api/autenticacao/registrar`
- Objetivo: criar usuário.
- Auth: não exige token.
- Body JSON:
  - `username` (string, obrigatório)
  - `password` (string, obrigatório)
  - `perfil` (string, opcional: `varejo`, `logistica`, `distribuicao`; padrão `varejo`)

### 3) `POST /api/autenticacao/login`
- Objetivo: autenticar e obter JWT.
- Auth: não exige token.
- Body JSON:
  - `username` (string, obrigatório)
  - `password` (string, obrigatório)
- Retorno: `access_token`.

### 4) `GET /api/combustivel/cenarios`
- Objetivo: retornar opções de formulário (selects, ranges e exemplos).
- Auth: exige JWT.
- Parâmetros: nenhum.

### 5) `POST /api/combustivel/predizer`
- Objetivo: predição unitária e persistência no banco.
- Auth: exige JWT.
- Body JSON:
  - `year` (int, obrigatório, 1924..2035)
  - `region` (string, obrigatório)
  - `subsidy_regime` (string, obrigatório: `none|partial|heavy`)
  - `is_oil_producer` (int, obrigatório: `0|1`)
  - `crude_oil_usd_per_barrel` (float, obrigatório, >= 0)
  - `tax_pct_of_pump_price` (float, obrigatório, 0..100)
  - `gasoline_real_2024usd` (float, obrigatório, >= 0)
  - `country` (string, opcional)
  - `segmento` (string, opcional: `varejo|logistica|distribuicao`)

### 6) `POST /api/combustivel/predizer-lote`
- Objetivo: predição de múltiplos cenários no mesmo request.
- Auth: exige JWT.
- Body JSON:
  - `items` (array obrigatório) com objetos no mesmo formato do endpoint unitário.

### 7) `GET /api/combustivel/predicoes/recentes`
- Objetivo: listar histórico recente de predições.
- Auth: exige JWT.
- Query params:
  - `limit` (int opcional, padrão `20`, min `1`, max `200`)

### 8) `GET /api/combustivel/insights/regioes`
- Objetivo: resumo por região e classe predita.
- Auth: exige JWT.
- Query params:
  - `country` (string, opcional)
  - `segmento` (string, opcional: `varejo|logistica|distribuicao`)

### 9) `GET /api/combustivel/insights/top-regioes-risco`
- Objetivo: ranking de regiões com maior concentração de risco alto.
- Auth: exige JWT.
- Query params:
  - `limit` (int opcional, padrão `5`, min `1`, max `50`)

### 10) `GET /api/combustivel/dashboard-executivo`
- Objetivo: KPIs executivos (volume, risco, região mais ativa, etc.).
- Auth: exige JWT.
- Parâmetros: nenhum.

### 11) `GET /api/combustivel/alertas`
- Objetivo: listar alertas ativos de risco.
- Auth: exige JWT.
- Parâmetros: nenhum.

### 12) `GET /api/mercado/comparativo`
- Objetivo: trazer série de mercado via yfinance.
- Auth: exige JWT.
- Query params:
  - `symbol` (string opcional, padrão `BZ=F`)
  - `period_days` (int opcional, padrão `30`)

### 13) `POST /api/modelos/registrar`
- Objetivo: registrar versão de modelo (MLOps).
- Auth: exige JWT com perfil `distribuicao`.
- Body JSON:
  - `version` (string, obrigatório)
  - `algorithm` (string, obrigatório)
  - `accuracy` (float, obrigatório)
  - `model_path` (string, obrigatório)

### 14) `POST /api/modelos/ativar`
- Objetivo: ativar versão de modelo com regra de acurácia e rollback lógico.
- Auth: exige JWT com perfil `distribuicao`.
- Body JSON:
  - `version` (string, obrigatório)
  - `min_accuracy` (float, opcional, padrão `0.8`)

### 15) `GET /api/modelos`
- Objetivo: listar histórico de versões de modelo.
- Auth: exige JWT.
- Parâmetros: nenhum.

## Token JWT

1. Faça login em `POST /api/autenticacao/login`.
2. Copie `access_token`.
3. Envie nas rotas protegidas:

```http
Authorization: Bearer SEU_TOKEN
```

## Guia rápido dos painéis da aplicação (SPA)

- **Home Executiva**: visão rápida do negócio com KPIs e gráficos (risco por região e distribuição por faixa de preço).
- **Predições**: formulário guiado para predição unitária e área de predição em lote.
- **Analytics**: consulta de histórico, insights por região, top regiões de risco e alertas.
- **Mercado Externo**: comparativo com série de ativo via `yfinance` (ex.: Brent/WTI/USD-BRL).
- **MLOps**: registro, ativação e listagem de versões de modelo (perfil `distribuicao`).

## Predição em lote (como usar)

Quando usar:
- simular vários cenários de uma vez;
- comparar impacto entre regiões e regimes;
- evitar enviar um request por cenário.

Endpoint:
- `POST /api/combustivel/predizer-lote`

Formato do payload:
```json
{
  "items": [
    {
      "year": 2024,
      "region": "Latin America",
      "subsidy_regime": "partial",
      "is_oil_producer": 1,
      "crude_oil_usd_per_barrel": 82.4,
      "tax_pct_of_pump_price": 22.0,
      "gasoline_real_2024usd": 1.15
    },
    {
      "year": 2024,
      "region": "Europe",
      "subsidy_regime": "none",
      "is_oil_producer": 0,
      "crude_oil_usd_per_barrel": 84.0,
      "tax_pct_of_pump_price": 48.0,
      "gasoline_real_2024usd": 1.85
    }
  ]
}
```

Resposta:
- `data`: lista dos cenários válidos processados com sucesso;
- `errors`: lista com itens inválidos (com índice e motivo do erro), sem interromper os demais.

Dica prática:
- na tela **Predições**, você pode colar JSON no bloco "Predição em Lote", executar e revisar sucesso/erro por item.

## Testes

```bash
cd backend
pytest -q
```

## Observação de segurança

Se o repositório já teve `.env` versionado no passado, o ideal é:
1. remover o arquivo do Git,
2. rotacionar chaves/tokens já expostos,
3. manter somente `.env.example` público.

## Evidências para a entrega

- Notebook do processo de ML (Colab): `notebooks/` + link público do Colab.
- Código full stack completo: `backend/` e `frontend/`.
- Testes automatizados com threshold: `backend/test/`.
- Documentação da API: `http://127.0.0.1:5000/apidocs`.

## Checklist final de submissão

- [ ] Link do repositório público no GitHub.
- [ ] Link do notebook no Colab (executável do início ao fim).
- [ ] Vídeo de até 3 minutos mostrando a aplicação funcionando.
- [ ] Confirmação de que `.env` não foi versionado.
- [ ] Execução de testes (`pytest`) com sucesso.

## Roteiro curto para vídeo (até 3 min)

1. Contexto do problema e dataset escolhido (classificação de `price_tier`).
2. Execução rápida da API e abertura do Swagger.
3. Fluxo de autenticação (registro/login) e uso do token JWT.
4. Predição unitária e predição em lote.
5. Dashboard/insights/alertas e exemplo de endpoint de mercado.
6. Teste automatizado de desempenho do modelo com PyTest.

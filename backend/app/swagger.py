def build_swagger_template():
    return {
        "swagger": "2.0",
        "info": {
            "title": "Fuel-Insight-MVP API",
            "version": "2.0.0",
            "description": (
                "Documentacao OpenAPI da API de combustivel, autenticacao e MLOps.\n\n"
                "COMO USAR TOKEN JWT:\n"
                "1. Execute POST /api/autenticacao/login.\n"
                "2. Copie o access_token retornado.\n"
                "3. Clique no botao Authorize no Swagger.\n"
                "4. Cole no formato: Bearer <seu_token_jwt>.\n"
                "5. Chame os endpoints protegidos normalmente.\n\n"
                "ROTAS PUBLICAS:\n"
                "- GET /api/saude\n"
                "- POST /api/autenticacao/registrar\n"
                "- POST /api/autenticacao/login\n\n"
                "ROTAS PROTEGIDAS:\n"
                "- Todas as rotas /api/combustivel/*\n"
                "- GET /api/mercado/comparativo\n"
                "- Rotas /api/modelos/*\n\n"
                "CAMPOS PRINCIPAIS DA PREDICAO:\n"
                "- year: ano do cenario\n"
                "- region: regiao geografica\n"
                "- country: pais para segmentacao (opcional)\n"
                "- segmento: varejo/logistica/distribuicao\n"
                "- subsidy_regime: none/partial/heavy\n"
                "- is_oil_producer: 0 ou 1\n"
                "- crude_oil_usd_per_barrel: preco do barril em USD\n"
                "- tax_pct_of_pump_price: imposto no preco da bomba\n"
                "- gasoline_real_2024usd: preco real em USD 2024\n"
            ),
        },
        "basePath": "/",
        "schemes": ["http"],
        "securityDefinitions": {
            "bearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Use: Bearer <seu_token_jwt>",
            }
        },
        "paths": {
            "/api/saude": {
                "get": {
                    "tags": ["Sistema"],
                    "summary": "Status da API",
                    "description": (
                        "Endpoint de health check.\n\n"
                        "COMO USAR:\n"
                        "- Chame sem token para verificar se o backend esta online.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Nao acessa banco nem modelo.\n"
                        "- Apenas confirma disponibilidade da aplicacao.\n\n"
                        "QUANDO USAR:\n"
                        "- Monitoramento, deploy e troubleshooting."
                    ),
                    "responses": {"200": {"description": "API online"}},
                }
            },
            "/api/autenticacao/registrar": {
                "post": {
                    "tags": ["Autenticacao"],
                    "summary": "Registrar usuario",
                    "description": (
                        "Cria um novo usuario para acessar a plataforma.\n\n"
                        "COMO USAR:\n"
                        "1) Envie username, password e perfil.\n"
                        "2) Se usuario nao existir, cadastro e confirmado.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Garante unicidade de username.\n"
                        "- Armazena senha com hash.\n"
                        "- Perfil define permissao funcional.\n\n"
                        "QUANDO USAR:\n"
                        "- Onboarding de novos usuarios internos."
                    ),
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string", "example": "analista01"},
                                    "password": {"type": "string", "example": "123456"},
                                    "perfil": {"type": "string", "enum": ["varejo", "logistica", "distribuicao"], "example": "varejo"},
                                },
                            },
                        }
                    ],
                    "responses": {"201": {"description": "Usuario criado"}},
                }
            },
            "/api/autenticacao/login": {
                "post": {
                    "tags": ["Autenticacao"],
                    "summary": "Login e token JWT",
                    "description": (
                        "Valida credenciais e devolve access_token JWT.\n\n"
                        "COMO USAR:\n"
                        "1) Envie username e password.\n"
                        "2) Copie access_token da resposta.\n"
                        "3) Use no header: Authorization: Bearer <token>.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Confere credenciais com hash de senha.\n"
                        "- Injeta claims de perfil no JWT.\n\n"
                        "QUANDO USAR:\n"
                        "- Antes de qualquer rota protegida."
                    ),
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                },
                            },
                        }
                    ],
                    "responses": {"200": {"description": "Login OK"}},
                }
            },
            "/api/combustivel/cenarios": {
                "get": {
                    "tags": ["Combustivel"],
                    "summary": "Lista cenarios e campos do formulario",
                    "description": (
                        "Entrega configuracao completa para formulario dinamico.\n\n"
                        "COMO USAR:\n"
                        "- Chame com JWT e use o retorno para montar selects/ranges no front.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Centraliza opcoes permitidas de dominio.\n"
                        "- Reduz erros de validacao no envio de predicoes.\n\n"
                        "QUANDO USAR:\n"
                        "- Inicializacao de telas e validacao cliente."
                    ),
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "Cenarios carregados"}},
                }
            },
            "/api/combustivel/predizer": {
                "post": {
                    "tags": ["Combustivel"],
                    "summary": "Predicao unitária",
                    "description": (
                        "Endpoint principal de negocio.\n\n"
                        "COMO USAR:\n"
                        "1) Garanta que esta autenticado com JWT (Authorization: Bearer ...).\n"
                        "2) Monte o payload com os campos obrigatorios.\n"
                        "3) Envie a requisicao.\n"
                        "4) A API valida os dados, executa o modelo e salva o resultado.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Valida regras de dominio (faixas, enums, campos obrigatorios).\n"
                        "- Calcula a classe prevista (price_tier).\n"
                        "- Persiste a predicao no banco para historico, insights e dashboard.\n"
                        "- Retorna objeto salvo com id, data e classe prevista.\n\n"
                        "QUANDO USAR:\n"
                        "- Simulacao unitária de cenario.\n"
                        "- Captura de predicao para trilha de auditoria.\n\n"
                        "ERROS COMUNS:\n"
                        "- 400: campo fora da faixa (ex: imposto > 100).\n"
                        "- 400: valor nao permitido (ex: segmento invalido).\n"
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "type": "object",
                                "required": [
                                    "year",
                                    "region",
                                    "subsidy_regime",
                                    "is_oil_producer",
                                    "crude_oil_usd_per_barrel",
                                    "tax_pct_of_pump_price",
                                    "gasoline_real_2024usd",
                                ],
                                "properties": {
                                    "year": {"type": "integer", "minimum": 1924, "maximum": 2035},
                                    "region": {
                                        "type": "string",
                                        "enum": [
                                            "Latin America",
                                            "North America",
                                            "Europe",
                                            "Asia",
                                            "Asia Pacific",
                                            "Middle East",
                                            "Africa",
                                            "Eurasia",
                                            "Europe/Asia",
                                        ],
                                    },
                                    "country": {"type": "string"},
                                    "segmento": {"type": "string", "enum": ["varejo", "logistica", "distribuicao"]},
                                    "subsidy_regime": {"type": "string", "enum": ["none", "partial", "heavy"]},
                                    "is_oil_producer": {"type": "integer", "enum": [0, 1]},
                                    "crude_oil_usd_per_barrel": {"type": "number", "minimum": 0},
                                    "tax_pct_of_pump_price": {"type": "number", "minimum": 0, "maximum": 100},
                                    "gasoline_real_2024usd": {"type": "number", "minimum": 0},
                                },
                            },
                        }
                    ],
                    "responses": {"200": {"description": "Predicao realizada"}},
                }
            },
            "/api/combustivel/predizer-lote": {
                "post": {
                    "tags": ["Combustivel"],
                    "summary": "Predicao em lote",
                    "description": (
                        "Processa varios cenarios no mesmo request.\n\n"
                        "COMO USAR:\n"
                        "1) Autentique com JWT.\n"
                        "2) Envie payload no formato: {\"items\": [cenario1, cenario2, ...]}.\n"
                        "3) Analise o retorno em dois blocos: data (sucesso) e errors (falhas por indice).\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Cada item eh validado individualmente.\n"
                        "- Itens validos sao preditos e persistidos.\n"
                        "- Itens invalidos nao bloqueiam o lote inteiro.\n"
                        "- A resposta final traz granularidade de erro por posicao.\n\n"
                        "QUANDO USAR:\n"
                        "- Importacao de cenarios em massa.\n"
                        "- Processamento de simulacoes de varias regioes/paises de uma vez.\n\n"
                        "DICA PRATICA:\n"
                        "- Use o endpoint /api/combustivel/cenarios para montar os selects e evitar erros de validacao.\n"
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "type": "object",
                                "properties": {"items": {"type": "array", "items": {"type": "object"}}},
                            },
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lote processado",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "message": {"type": "string"},
                                    "data": {"type": "array", "items": {"type": "object"}},
                                    "errors": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {"index": {"type": "integer"}, "error": {"type": "object"}},
                                        },
                                    },
                                },
                            },
                        }
                    },
                }
            },
            "/api/combustivel/predicoes/recentes": {
                "get": {
                    "tags": ["Combustivel"],
                    "summary": "Historico recente",
                    "description": (
                        "Consulta as ultimas predicoes gravadas.\n\n"
                        "COMO USAR:\n"
                        "- Informe limit para controlar volume retornado.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Ordena por data mais recente.\n"
                        "- Facilita rastreabilidade e auditoria operacional.\n\n"
                        "QUANDO USAR:\n"
                        "- Timeline, debug e painel historico."
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [{"in": "query", "name": "limit", "type": "integer", "default": 20}],
                    "responses": {"200": {"description": "Historico carregado"}},
                }
            },
            "/api/combustivel/insights/regioes": {
                "get": {
                    "tags": ["Insights"],
                    "summary": "Resumo por regiao",
                    "description": (
                        "Agrega predições por regiao e classe prevista.\n\n"
                        "COMO USAR:\n"
                        "- Opcionalmente informe country e segmento para segmentar visao.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Faz agrupamento por regiao + classe.\n"
                        "- Calcula quantidade e media de preco real.\n\n"
                        "QUANDO USAR:\n"
                        "- Analise regional e comparativo comercial."
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "country", "type": "string"},
                        {"in": "query", "name": "segmento", "type": "string", "enum": ["varejo", "logistica", "distribuicao"]},
                    ],
                    "responses": {"200": {"description": "Resumo carregado"}},
                }
            },
            "/api/combustivel/insights/top-regioes-risco": {
                "get": {
                    "tags": ["Insights"],
                    "summary": "Ranking de risco alto",
                    "description": (
                        "Mostra regioes com maior concentracao de classes de risco alto.\n\n"
                        "COMO USAR:\n"
                        "- Ajuste limit para definir tamanho do ranking.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Considera classes High e Very High.\n"
                        "- Ordena por maior volume de risco.\n\n"
                        "QUANDO USAR:\n"
                        "- Priorizar acoes comerciais e mitigacao."
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [{"in": "query", "name": "limit", "type": "integer", "default": 5}],
                    "responses": {"200": {"description": "Ranking carregado"}},
                }
            },
            "/api/combustivel/dashboard-executivo": {
                "get": {
                    "tags": ["Comercial"],
                    "summary": "KPIs executivos",
                    "description": (
                        "Painel executivo consolidado de negocio.\n\n"
                        "COMO USAR:\n"
                        "- Chame para obter indicadores prontos para diretoria.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Consolida risco alto, volume, regiao destaque.\n"
                        "- Inclui volatilidade externa e acuracia historica.\n\n"
                        "QUANDO USAR:\n"
                        "- Reunioes gerenciais e acompanhamento de performance."
                    ),
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "Dashboard gerado"}},
                }
            },
            "/api/combustivel/alertas": {
                "get": {
                    "tags": ["Comercial"],
                    "summary": "Alertas ativos",
                    "description": (
                        "Gera alertas acionaveis de risco alto.\n\n"
                        "COMO USAR:\n"
                        "- Consulte periodicamente para detectar pontos criticos.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Avalia concentracao de previsoes caras por regiao.\n"
                        "- Retorna severidade e contexto para acao.\n\n"
                        "QUANDO USAR:\n"
                        "- Operacao comercial e monitoramento continuo."
                    ),
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "Alertas processados"}},
                }
            },
            "/api/mercado/comparativo": {
                "get": {
                    "tags": ["Mercado"],
                    "summary": "Serie comparativa via yfinance",
                    "description": (
                        "Busca serie de ativo externo via yfinance.\n\n"
                        "COMO USAR:\n"
                        "- Informe symbol e period_days.\n"
                        "- Use pontos retornados para grafico no frontend.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Coleta fechamento diario.\n"
                        "- Calcula variacao percentual no periodo.\n\n"
                        "QUANDO USAR:\n"
                        "- Correlacao entre mercado externo e predicoes internas."
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "symbol", "type": "string", "default": "BZ=F"},
                        {"in": "query", "name": "period_days", "type": "integer", "default": 30},
                    ],
                    "responses": {"200": {"description": "Serie carregada"}},
                }
            },
            "/api/modelos/registrar": {
                "post": {
                    "tags": ["MLOps"],
                    "summary": "Registrar versao de modelo",
                    "description": (
                        "Registra metadados de uma nova versao de modelo.\n\n"
                        "COMO USAR:\n"
                        "- Envie version, algorithm, accuracy e model_path.\n"
                        "- Requer perfil distribuicao.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Mantem trilha de governanca e auditoria de modelos.\n"
                        "- Nao ativa automaticamente a versao.\n\n"
                        "QUANDO USAR:\n"
                        "- Pos treino/aprovacao de nova versao."
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "type": "object",
                                "required": ["version", "algorithm", "accuracy", "model_path"],
                                "properties": {
                                    "version": {"type": "string"},
                                    "algorithm": {"type": "string"},
                                    "accuracy": {"type": "number"},
                                    "model_path": {"type": "string"},
                                },
                            },
                        }
                    ],
                    "responses": {"201": {"description": "Versao registrada"}},
                }
            },
            "/api/modelos/ativar": {
                "post": {
                    "tags": ["MLOps"],
                    "summary": "Ativar modelo com rollback",
                    "description": (
                        "Ativa versao de modelo com regra de seguranca.\n\n"
                        "COMO USAR:\n"
                        "- Envie version e opcionalmente min_accuracy.\n"
                        "- Requer perfil distribuicao.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Bloqueia ativacao se acuracia ficar abaixo do limite.\n"
                        "- Desativa versao ativa anterior (rollback logico).\n\n"
                        "QUANDO USAR:\n"
                        "- Promocao controlada de modelo em producao."
                    ),
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "type": "object",
                                "required": ["version"],
                                "properties": {"version": {"type": "string"}, "min_accuracy": {"type": "number", "default": 0.8}},
                            },
                        }
                    ],
                    "responses": {"200": {"description": "Modelo ativado"}},
                }
            },
            "/api/modelos": {
                "get": {
                    "tags": ["MLOps"],
                    "summary": "Listar versoes de modelo",
                    "description": (
                        "Lista historico de modelos registrados.\n\n"
                        "COMO USAR:\n"
                        "- Chame para ver status ativo/inativo de cada versao.\n\n"
                        "LOGICA DE NEGOCIO:\n"
                        "- Ordena por data de treino.\n"
                        "- Exibe metadados para governanca.\n\n"
                        "QUANDO USAR:\n"
                        "- Auditoria e acompanhamento de ciclo de vida de modelo."
                    ),
                    "security": [{"bearerAuth": []}],
                    "responses": {"200": {"description": "Lista carregada"}},
                }
            },
        },
    }

import uuid

from app.core import predictor
from app.services.market_service import MarketService


VALID_PAYLOAD = {
    "year": 2023,
    "region": "Latin America",
    "subsidy_regime": "partial",
    "is_oil_producer": 1,
    "crude_oil_usd_per_barrel": 80.0,
    "tax_pct_of_pump_price": 22.0,
    "gasoline_real_2024usd": 1.15,
}


def _auth_header(client, perfil="varejo"):
    username = f"user_{perfil}_{uuid.uuid4().hex[:8]}"
    password = "123456"
    reg = client.post(
        "/api/autenticacao/registrar",
        json={"username": username, "password": password, "perfil": perfil},
    )
    assert reg.status_code == 201
    login = client.post("/api/autenticacao/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    response = client.get("/api/saude")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert "mensagem" in response.json


def test_predict_success(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(predictor, "predict", lambda payload: "High ($1.10–$1.60)")
    response = client.post("/api/combustivel/predizer", json=VALID_PAYLOAD, headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Predicao realizada com sucesso"
    assert response.json["data"]["predicted_price_tier"] == "High ($1.10–$1.60)"


def test_predict_validation_error(client):
    headers = _auth_header(client)
    bad = dict(VALID_PAYLOAD)
    bad["tax_pct_of_pump_price"] = 120
    response = client.post("/api/combustivel/predizer", json=bad, headers=headers)
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Erro de validacao"


def test_batch_predict_mixed(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(predictor, "predict", lambda payload: "Very High (>$1.60)")
    payload = {
        "items": [
            VALID_PAYLOAD,
            {**VALID_PAYLOAD, "is_oil_producer": 2},
        ]
    }
    response = client.post("/api/combustivel/predizer-lote", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Predicao em lote finalizada"
    assert len(response.json["data"]) == 1
    assert len(response.json["errors"]) == 1


def test_recent_predictions_limit_validation(client):
    headers = _auth_header(client)
    response = client.get("/api/combustivel/predicoes/recentes?limit=0", headers=headers)
    assert response.status_code == 400
    assert response.json["success"] is False
    assert "limit" in response.json["message"]


def test_recent_predictions_success(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(predictor, "predict", lambda payload: "Very High (>$1.60)")
    client.post("/api/combustivel/predizer", json=VALID_PAYLOAD, headers=headers)

    response = client.get("/api/combustivel/predicoes/recentes?limit=5", headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Historico recente carregado"
    assert isinstance(response.json["data"], list)


def test_insights_endpoints(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(predictor, "predict", lambda payload: "Very High (>$1.60)")
    client.post("/api/combustivel/predizer", json=VALID_PAYLOAD, headers=headers)
    client.post("/api/combustivel/predizer", json={**VALID_PAYLOAD, "region": "Europe"}, headers=headers)

    region_response = client.get("/api/combustivel/insights/regioes", headers=headers)
    risk_response = client.get("/api/combustivel/insights/top-regioes-risco?limit=3", headers=headers)

    assert region_response.status_code == 200
    assert risk_response.status_code == 200
    assert region_response.json["success"] is True
    assert risk_response.json["success"] is True
    assert region_response.json["message"] == "Resumo regional gerado"
    assert risk_response.json["message"] == "Ranking de risco gerado"


def test_mercado_comparativo_success(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(
        MarketService,
        "compare_market",
        lambda symbol, period_days: {
            "symbol": symbol,
            "period_days": period_days,
            "inicio_preco": 70.0,
            "fim_preco": 75.0,
            "variacao_pct": 7.14,
            "pontos": [{"date": "2025-01-01", "close": 70.0}, {"date": "2025-01-02", "close": 75.0}],
        },
    )
    response = client.get("/api/mercado/comparativo?symbol=BZ=F&period_days=30", headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Serie de mercado carregada"
    assert response.json["data"]["symbol"] == "BZ=F"


def test_mercado_comparativo_bad_request(client, monkeypatch):
    headers = _auth_header(client)
    def _raise(symbol, period_days):
        raise ValueError("erro fake de mercado")

    monkeypatch.setattr(MarketService, "compare_market", _raise)
    response = client.get("/api/mercado/comparativo?symbol=BZ=F&period_days=2", headers=headers)
    assert response.status_code == 400
    assert response.json["success"] is False


def test_mercado_comparativo_external_failure(client, monkeypatch):
    headers = _auth_header(client)

    def _raise(symbol, period_days):
        raise RuntimeError("falha externa")

    monkeypatch.setattr(MarketService, "compare_market", _raise)
    response = client.get("/api/mercado/comparativo?symbol=USDBRL=X&period_days=7", headers=headers)
    assert response.status_code == 502
    assert response.json["success"] is False
    assert "Fonte externa indisponível" in response.json["message"]


def test_cenarios_endpoint(client):
    headers = _auth_header(client)
    response = client.get("/api/combustivel/cenarios", headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert "region_options" in response.json["data"]
    assert "country_options" in response.json["data"]
    assert isinstance(response.json["data"]["country_options"], list)
    assert "field_help" in response.json["data"]


def test_dashboard_executivo_endpoint(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(predictor, "predict", lambda payload: "Very High (>$1.60)")
    client.post("/api/combustivel/predizer", json=VALID_PAYLOAD, headers=headers)
    response = client.get("/api/combustivel/dashboard-executivo", headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Dashboard executivo gerado"
    assert "total_predicoes" in response.json["data"]


def test_alertas_endpoint(client, monkeypatch):
    headers = _auth_header(client)
    monkeypatch.setattr(predictor, "predict", lambda payload: "Very High (>$1.60)")
    client.post("/api/combustivel/predizer", json=VALID_PAYLOAD, headers=headers)
    client.post(
        "/api/combustivel/predizer",
        json={**VALID_PAYLOAD, "region": "Latin America", "year": 2025},
        headers=headers,
    )
    response = client.get("/api/combustivel/alertas", headers=headers)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Alertas processados"
    assert isinstance(response.json["data"], list)


def test_autenticacao_login_invalido(client):
    response = client.post("/api/autenticacao/login", json={"username": "x", "password": "errada"})
    assert response.status_code == 401
    assert response.json["success"] is False


def test_model_registry_fluxo_com_rollback(client):
    headers_admin = _auth_header(client, perfil="distribuicao")
    headers_user = _auth_header(client, perfil="varejo")

    forbidden = client.post(
        "/api/modelos/registrar",
        json={"version": "v1", "algorithm": "DecisionTree", "accuracy": 0.9, "model_path": "x.pkl"},
        headers=headers_user,
    )
    assert forbidden.status_code == 403

    reg1 = client.post(
        "/api/modelos/registrar",
        json={"version": "v1", "algorithm": "DecisionTree", "accuracy": 0.91, "model_path": "v1.pkl"},
        headers=headers_admin,
    )
    assert reg1.status_code == 201

    reg2 = client.post(
        "/api/modelos/registrar",
        json={"version": "v2", "algorithm": "SVM", "accuracy": 0.95, "model_path": "v2.pkl"},
        headers=headers_admin,
    )
    assert reg2.status_code == 201

    ativar_v1 = client.post("/api/modelos/ativar", json={"version": "v1", "min_accuracy": 0.8}, headers=headers_admin)
    assert ativar_v1.status_code == 200

    ativar_v2 = client.post("/api/modelos/ativar", json={"version": "v2", "min_accuracy": 0.8}, headers=headers_admin)
    assert ativar_v2.status_code == 200
    assert ativar_v2.json["data"]["rollback_de"] == "v1"

    lista = client.get("/api/modelos", headers=headers_admin)
    assert lista.status_code == 200
    assert lista.json["success"] is True


def test_api_fluxo_completo_por_regioes(client, monkeypatch):
    headers = _auth_header(client, perfil="distribuicao")
    monkeypatch.setattr(predictor, "predict", lambda payload: "High ($1.10–$1.60)")

    # Health
    health = client.get("/api/saude")
    assert health.status_code == 200

    # Cenarios
    cenarios = client.get("/api/combustivel/cenarios", headers=headers)
    assert cenarios.status_code == 200
    assert cenarios.json["success"] is True
    regions = cenarios.json["data"]["region_options"]
    assert isinstance(regions, list)
    assert len(regions) > 0

    # Predicoes em multiplas regioes validas (inclui country omitido para evitar erro de validacao)
    for idx, region in enumerate(regions[:4]):
        payload = {
            **VALID_PAYLOAD,
            "year": 2023 + idx,
            "region": region,
        }
        resp = client.post("/api/combustivel/predizer", json=payload, headers=headers)
        assert resp.status_code == 200
        assert resp.json["success"] is True

    # Endpoints analiticos/comerciais
    recent = client.get("/api/combustivel/predicoes/recentes?limit=10", headers=headers)
    insights = client.get("/api/combustivel/insights/regioes", headers=headers)
    risk = client.get("/api/combustivel/insights/top-regioes-risco?limit=5", headers=headers)
    dashboard = client.get("/api/combustivel/dashboard-executivo", headers=headers)
    alerts = client.get("/api/combustivel/alertas", headers=headers)

    assert recent.status_code == 200
    assert insights.status_code == 200
    assert risk.status_code == 200
    assert dashboard.status_code == 200
    assert alerts.status_code == 200

    # Mercado (mock)
    monkeypatch.setattr(
        MarketService,
        "compare_market",
        lambda symbol, period_days: {
            "symbol": symbol,
            "period_days": period_days,
            "inicio_preco": 70.0,
            "fim_preco": 72.0,
            "variacao_pct": 2.85,
            "pontos": [{"date": "2025-01-01", "close": 70.0}, {"date": "2025-01-02", "close": 72.0}],
        },
    )
    mercado = client.get("/api/mercado/comparativo?symbol=BZ=F&period_days=30", headers=headers)
    assert mercado.status_code == 200
    assert mercado.json["success"] is True

    # MLOps
    reg = client.post(
        "/api/modelos/registrar",
        json={"version": "v-full", "algorithm": "SVM", "accuracy": 0.95, "model_path": "v-full.pkl"},
        headers=headers,
    )
    assert reg.status_code == 201

    ativar = client.post("/api/modelos/ativar", json={"version": "v-full", "min_accuracy": 0.8}, headers=headers)
    assert ativar.status_code == 200
    lista = client.get("/api/modelos", headers=headers)
    assert lista.status_code == 200

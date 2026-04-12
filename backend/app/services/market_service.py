from datetime import UTC, datetime, timedelta

import yfinance as yf


class MarketService:
    @staticmethod
    def _fetch_history(symbol: str, period_days: int):
        end_date = datetime.now(UTC).date()
        start_date = end_date - timedelta(days=period_days + 10)

        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date.isoformat(), end=end_date.isoformat(), interval="1d")
        if hist is not None and not hist.empty and "Close" in hist.columns:
            return hist

        # Fallback mais resiliente quando o range por datas falha para alguns ativos.
        fallback_days = max(period_days * 4, 30)
        hist = yf.download(symbol, period=f"{fallback_days}d", interval="1d", progress=False, auto_adjust=False)
        if hist is not None and not hist.empty and "Close" in hist.columns:
            return hist

        # Segunda tentativa com history por periodo.
        hist = ticker.history(period=f"{fallback_days}d", interval="1d")
        if hist is not None and not hist.empty and "Close" in hist.columns:
            return hist

        raise RuntimeError(f"Nao foi possivel obter dados de mercado para o ativo {symbol}.")

    @staticmethod
    def compare_market(symbol: str = "BZ=F", period_days: int = 30) -> dict:
        symbol = (symbol or "").strip()
        if not symbol:
            raise ValueError("symbol e obrigatorio.")
        if period_days < 7 or period_days > 365:
            raise ValueError("period_days precisa ser entre 7 e 365.")

        hist = MarketService._fetch_history(symbol, period_days)

        closes = hist["Close"].dropna()
        if closes.empty:
            raise RuntimeError(f"Serie de preco vazia para {symbol}.")

        closes = closes.tail(max(2, period_days))
        if len(closes) < 2:
            raise RuntimeError(f"Historico insuficiente para o ativo {symbol}.")
        initial = float(closes.iloc[0])
        final = float(closes.iloc[-1])
        var_pct = ((final - initial) / initial) * 100 if initial else 0.0

        points = [{"date": idx.strftime("%Y-%m-%d"), "close": float(value)} for idx, value in closes.items()]
        return {
            "symbol": symbol,
            "period_days": period_days,
            "inicio_preco": initial,
            "fim_preco": final,
            "variacao_pct": var_pct,
            "pontos": points,
        }

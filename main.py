from websocket import WebSocketApp
import json
import time

# ✅ CONFIGURAÇÕES DO BOT
modo = "DEMO"  # ou "REAL"
api_token_demo = "UkoPGTDMuHHLB8Y" 
api_token_real = "AQUI_VAI_SEU_TOKEN_REAL"
ativo = "R_75"  # Ativo de índice sintético
api_token = api_token_demo if modo == "DEMO" else api_token_real

# ✅ VARIÁVEL PARA ARMAZENAR VELAS
ultimas_velas = []

# ✅ FUNÇÃO AO CONECTAR
def ao_abrir(ws):
    print("🔗 Conectado à Deriv!")
    auth = {"authorize": api_token}
    ws.send(json.dumps(auth))

# ✅ FUNÇÃO AO RECEBER MENSAGEM
def ao_receber(ws, mensagem):
    dados = json.loads(mensagem)
    if 'authorize' in dados:
        print("🔐 Autorizado! Recebendo candles...")
        sub = {
            "ticks_history": ativo,
            "style": "candles",
            "granularity": 1,
            "count": 5,
            "subscribe": 1
        }
        ws.send(json.dumps(sub))

    elif 'candles' in dados:
        candles = dados['candles']
        for candle in candles:
            processar_candle(candle)

    elif 'ohlc' in dados:
        candle = dados['ohlc']
        processar_candle(candle)

# ✅ PROCESSADOR DE CANDLE
def processar_candle(candle):
    analise = analisar_candle(candle)
    ultimas_velas.append(analise)
    if len(ultimas_velas) > 3:
        ultimas_velas.pop(0)
    if detectar_exaustao(ultimas_velas):
        validador_de_entrada(ultimas_velas)

# ✅ FUNÇÃO AO FECHAR
def ao_fechar(ws, close_status_code, close_msg):
    print("🔌 Conexão encerrada.")

# ✅ FUNÇÃO DE ERRO
def ao_erro(ws, error):
    print(f"❌ Erro: {error}")

# ✅ FUNÇÃO DE ANÁLISE
def analisar_candle(candle):
    open_ = float(candle["open"])
    close = float(candle["close"])
    high = float(candle["high"])
    low = float(candle["low"])

    corpo = abs(close - open_)
    sombra_sup = high - max(open_, close)
    sombra_inf = min(open_, close) - low

    direcao = "alta" if close > open_ else "baixa"
    rejeicao = "nenhuma"
    if sombra_sup > corpo * 2:
        rejeicao = "rejeição de alta"
    elif sombra_inf > corpo * 2:
        rejeicao = "rejeição de baixa"

    print(f"📊 Vela: {direcao} | Corpo: {round(corpo, 3)} | Rejeição: {rejeicao}")
    return {
        "direcao": direcao,
        "corpo": corpo,
        "rejeicao": rejeicao
    }

# ✅ DETECTOR DE EXAUSTÃO
def detectar_exaustao(velas):
    if len(velas) < 3:
        return False
    v1, v2, v3 = velas[-3], velas[-2], velas[-1]
    corpo_medio = (v1["corpo"] + v2["corpo"]) / 2
    exausto = v3["corpo"] < corpo_medio * 0.6 and v3["rejeicao"] != "nenhuma"
    if exausto:
        print("⚠️ Exaustão + Rejeição Detectada")
    return exausto

# ✅ VALIDADOR DE ENTRADA
def validador_de_entrada(velas):
    v1, v2, v3 = velas[-3], velas[-2], velas[-1]
    direcao_previa = v1["direcao"]
    direcao_atual = v3["direcao"]
    if direcao_previa != direcao_atual:
        print("✅ ENTRADA VALIDADA: Direção mudou após exaustão")
    else:
        print("⛔ Entrada Rejeitada: sem mudança de direção")

# ✅ INICIAR CONEXÃO
def iniciar_conexao():
    socket = "wss://ws.derivws.com/websockets/v3"
    ws = WebSocketApp(
        socket,
        on_open=ao_abrir,
        on_message=ao_receber,
        on_close=ao_fechar,
        on_error=ao_erro
    )
    ws.run_forever()

# ✅ EXECUTAR O BOT
def executar_operacao():
    print("🚀 Iniciando bot de trading Deriv...")
    try:
        iniciar_conexao()
    except KeyboardInterrupt:
        print("🛑 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro no bot: {e}")

# ✅ EXECUTAR SCRIPT PRINCIPAL
if __name__ == "__main__":
    executar_operacao()

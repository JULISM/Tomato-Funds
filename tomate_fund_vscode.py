# ============================================
# SISTEMA TOMATE FUND - API FLASK
# Versão corrigida e preparada para Render
# ============================================

from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from datetime import datetime
import uuid

# ============================================
# DADOS EM MEMÓRIA (SIMULANDO BANCO)
# ============================================

FUNDOS_DATA = {
    "1": {
        "id": "1",
        "nome": "FIP Tech Innovation",
        "cnpj": "12.345.678/0001-90",
        "patrimonio": 50000000.00,
        "criado_em": "2024-01-01"
    }
}

# ============================================
# BLUEPRINT DA API
# ============================================

tomate_fund_bp = Blueprint("tomate_fund", __name__)

@tomate_fund_bp.route("/fundos", methods=["GET"])
def listar_fundos():
    return jsonify(list(FUNDOS_DATA.values()))

@tomate_fund_bp.route("/fundos", methods=["POST"])
def criar_fundo():
    data = request.json
    fundo_id = str(uuid.uuid4())

    FUNDOS_DATA[fundo_id] = {
        "id": fundo_id,
        "nome": data.get("nome"),
        "cnpj": data.get("cnpj"),
        "patrimonio": float(data.get("patrimonio", 0)),
        "criado_em": datetime.now().strftime("%Y-%m-%d")
    }

    return jsonify({
        "success": True,
        "fundo": FUNDOS_DATA[fundo_id]
    }), 201

@tomate_fund_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API Tomate Fund funcionando",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

# ============================================
# HTML EMBUTIDO (FRONT SIMPLES)
# ============================================

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Tomato Fund</title>
</head>
<body>
    <h1>🍅 Tomato Fund</h1>
    <p>API rodando com sucesso.</p>
</body>
</html>
"""

# ============================================
# APP PRINCIPAL
# ============================================

app = Flask(__name__)
app.config["SECRET_KEY"] = "tomate_fund_secret_key_2024"

CORS(app)

app.register_blueprint(tomate_fund_bp, url_prefix="/api")

@app.route("/")
def serve_index():
    return HTML_CONTENT

# ============================================
# ENTRYPOINT LOCAL
# ============================================

if __name__ == "__main__":
    print("🍅 Tomate Fund rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

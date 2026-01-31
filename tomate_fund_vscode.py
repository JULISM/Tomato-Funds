# SISTEMA TOMATE FUND - API COMPLETA EM PYTHON (FLASK)
# Versão 3.0 - Com CRUD de Fundos e Relatórios Personalizados
from flask import Flask, jsonify, request, Blueprint, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import uuid

# =========================================================
# 1. LÓGICA DE NEGÓCIOS (SIMULANDO BANCO DE DADOS)
# =========================================================

# Dados dos fundos (mutável para CRUD)
FUNDOS_DATA = {
    "1": {
        "id": "1",
        "nome": "FIP Tech Innovation",
        "cnpj": "12.345.678/0001-90",
        "patrimonio": 50000000.00,
        "liquidez": 5000000.00,
        "politica_liquidez": "Ativos de Risco",
        "prazo_resgate": 30,
        "gestor": "Tomate Capital",
        "taxa_admin": 2.5,
        "data_criacao": "2024-01-15",
        "status": "ATIVO"
    },
    "2": {
        "id": "2", 
        "nome": "FIDC Recebíveis",
        "cnpj": "98.765.432/0001-10",
        "patrimonio": 75000000.00,
        "liquidez": 7500000.00,
        "politica_liquidez": "Livre de Risco",
        "prazo_resgate": 15,
        "gestor": "Tomate Asset",
        "taxa_admin": 1.8,
        "data_criacao": "2024-02-20",
        "status": "ATIVO"
    }
}

# Compromissos de pagamento
COMPROMISSOS_DATA = [
    {
        "id": 1,
        "fundo_id": "1",
        "tipo": "Taxa Administração",
        "valor": 125000.00,
        "vencimento": "2025-01-20",
        "status": "PENDENTE",
        "descricao": "Taxa de administração mensal"
    },
    {
        "id": 2,
        "fundo_id": "1", 
        "tipo": "Debênture ABC Corp",
        "valor": 500000.00,
        "vencimento": "2025-01-22",
        "status": "PENDENTE",
        "descricao": "Pagamento de juros debênture"
    },
    {
        "id": 3,
        "fundo_id": "2",
        "tipo": "Taxa Performance",
        "valor": 250000.00,
        "vencimento": "2025-01-25",
        "status": "PENDENTE",
        "descricao": "Taxa de performance trimestral"
    },
    {
        "id": 4,
        "fundo_id": "1",
        "tipo": "SPA Pagamento",
        "valor": 300000.00,
        "vencimento": "2025-02-01",
        "status": "PENDENTE",
        "descricao": "Parcela SPA aquisição"
    }
]

# Recebimentos esperados
RECEBIMENTOS_DATA = [
    {
        "id": 1,
        "fundo_id": "1",
        "tipo": "Debênture XYZ Corp",
        "valor": 300000.00,
        "vencimento": "2025-01-24",
        "status": "PENDENTE",
        "descricao": "Recebimento de juros"
    },
    {
        "id": 2,
        "fundo_id": "2",
        "tipo": "Recebível Comercial",
        "valor": 200000.00,
        "vencimento": "2025-01-28",
        "status": "PENDENTE",
        "descricao": "Recebível de duplicatas"
    },
    {
        "id": 3,
        "fundo_id": "1",
        "tipo": "CRI Imobiliário",
        "valor": 150000.00,
        "vencimento": "2025-02-03",
        "status": "PENDENTE",
        "descricao": "Certificado de Recebível Imobiliário"
    },
    {
        "id": 4,
        "fundo_id": "2",
        "tipo": "Nota Comercial",
        "valor": 100000.00,
        "vencimento": "2025-02-10",
        "status": "PENDENTE",
        "descricao": "Vencimento nota comercial"
    }
]

# Subscrições de cotistas
SUBSCRICOES_DATA = [
    {
        "id": 1,
        "fundo_id": "1",
        "cotista": "João Silva",
        "cpf_cnpj": "123.456.789-00",
        "cotas": 1000,
        "valor_parcela": 100000.00,
        "vencimento": "2025-01-30",
        "status": "PENDENTE",
        "parcela": "1/3"
    },
    {
        "id": 2,
        "fundo_id": "2",
        "cotista": "Maria Santos", 
        "cpf_cnpj": "987.654.321-00",
        "cotas": 500,
        "valor_parcela": 50000.00,
        "vencimento": "2025-02-05",
        "status": "PENDENTE",
        "parcela": "2/5"
    },
    {
        "id": 3,
        "fundo_id": "1",
        "cotista": "Empresa ABC Ltda",
        "cpf_cnpj": "11.222.333/0001-44",
        "cotas": 2000,
        "valor_parcela": 200000.00,
        "vencimento": "2025-02-12",
        "status": "PENDENTE",
        "parcela": "1/2"
    }
]

# =========================================================
# 2. ROTAS DA API (BLUEPRINT)
# =========================================================

tomate_fund_bp = Blueprint('tomate_fund', __name__)

# --- ROTAS CRUD PARA FUNDOS ---

@tomate_fund_bp.route('/fundos', methods=['GET'])
def get_fundos():
    """Listar todos os fundos"""
    return jsonify({
        "success": True,
        "data": list(FUNDOS_DATA.values()),
        "total": len(FUNDOS_DATA)
    })

@tomate_fund_bp.route('/fundos/<fundo_id>', methods=['GET'])
def get_fundo(fundo_id):
    """Obter detalhes de um fundo específico"""
    if fundo_id not in FUNDOS_DATA:
        return jsonify({"success": False, "error": "Fundo não encontrado"}), 404
    
    return jsonify({
        "success": True,
        "data": FUNDOS_DATA[fundo_id]
    })

@tomate_fund_bp.route('/fundos', methods=['POST'])
def criar_fundo():
    """Criar um novo fundo"""
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        campos_obrigatorios = ['nome', 'cnpj', 'patrimonio', 'liquidez', 'politica_liquidez', 'gestor', 'taxa_admin']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({"success": False, "error": f"Campo '{campo}' é obrigatório"}), 400
        
        # Gerar ID único
        novo_id = str(len(FUNDOS_DATA) + 1)
        while novo_id in FUNDOS_DATA:
            novo_id = str(int(novo_id) + 1)
        
        # Criar novo fundo
        novo_fundo = {
            "id": novo_id,
            "nome": data['nome'],
            "cnpj": data['cnpj'],
            "patrimonio": float(data['patrimonio']),
            "liquidez": float(data['liquidez']),
            "politica_liquidez": data['politica_liquidez'],
            "prazo_resgate": int(data.get('prazo_resgate', 30)),
            "gestor": data['gestor'],
            "taxa_admin": float(data['taxa_admin']),
            "data_criacao": datetime.now().strftime("%Y-%m-%d"),
            "status": "ATIVO"
        }
        
        # Adicionar ao "banco de dados"
        FUNDOS_DATA[novo_id] = novo_fundo
        
        return jsonify({
            "success": True,
            "message": "Fundo criado com sucesso!",
            "data": novo_fundo
        }), 201
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tomate_fund_bp.route('/fundos/<fundo_id>', methods=['PUT'])
def atualizar_fundo(fundo_id):
    """Atualizar um fundo existente"""
    try:
        if fundo_id not in FUNDOS_DATA:
            return jsonify({"success": False, "error": "Fundo não encontrado"}), 404
        
        data = request.get_json()
        fundo = FUNDOS_DATA[fundo_id]
        
        # Atualizar campos fornecidos
        campos_atualizaveis = ['nome', 'cnpj', 'patrimonio', 'liquidez', 'politica_liquidez', 'prazo_resgate', 'gestor', 'taxa_admin', 'status']
        for campo in campos_atualizaveis:
            if campo in data:
                if campo in ['patrimonio', 'liquidez', 'taxa_admin']:
                    fundo[campo] = float(data[campo])
                elif campo == 'prazo_resgate':
                    fundo[campo] = int(data[campo])
                else:
                    fundo[campo] = data[campo]
        
        return jsonify({
            "success": True,
            "message": "Fundo atualizado com sucesso!",
            "data": fundo
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tomate_fund_bp.route('/fundos/<fundo_id>', methods=['DELETE'])
def deletar_fundo(fundo_id):
    """Deletar um fundo"""
    try:
        if fundo_id not in FUNDOS_DATA:
            return jsonify({"success": False, "error": "Fundo não encontrado"}), 404
        
        fundo_deletado = FUNDOS_DATA.pop(fundo_id)
        
        # Remover dados relacionados ao fundo (simulação)
        global COMPROMISSOS_DATA, RECEBIMENTOS_DATA, SUBSCRICOES_DATA
        COMPROMISSOS_DATA = [c for c in COMPROMISSOS_DATA if c["fundo_id"] != fundo_id]
        RECEBIMENTOS_DATA = [r for r in RECEBIMENTOS_DATA if r["fundo_id"] != fundo_id]
        SUBSCRICOES_DATA = [s for s in SUBSCRICOES_DATA if s["fundo_id"] != fundo_id]
        
        return jsonify({
            "success": True,
            "message": f"Fundo '{fundo_deletado['nome']}' deletado com sucesso!"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- ROTAS DE RELATÓRIOS ---

@tomate_fund_bp.route('/relatorios/gerar', methods=['POST'])
def gerar_relatorio_personalizado():
    """Gerar relatório personalizado"""
    try:
        data = request.get_json()
        tipo_relatorio = data.get('tipo', 'completo')
        fundo_ids = data.get('fundos', list(FUNDOS_DATA.keys()))
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        relatorio = {
            "tipo": tipo_relatorio,
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            },
            "fundos_analisados": len(fundo_ids),
            "dados": {}
        }
        
        if tipo_relatorio in ['completo', 'fundos']:
            # Dados dos fundos
            fundos_selecionados = {k: v for k, v in FUNDOS_DATA.items() if k in fundo_ids}
            relatorio["dados"]["fundos"] = list(fundos_selecionados.values())
            
            # Estatísticas dos fundos
            total_patrimonio = sum([f["patrimonio"] for f in fundos_selecionados.values()])
            total_liquidez = sum([f["liquidez"] for f in fundos_selecionados.values()])
            
            relatorio["dados"]["estatisticas_fundos"] = {
                "total_patrimonio": total_patrimonio,
                "total_liquidez": total_liquidez,
                "patrimonio_medio": total_patrimonio / len(fundos_selecionados) if fundos_selecionados else 0,
                "liquidez_media": total_liquidez / len(fundos_selecionados) if fundos_selecionados else 0
            }
        
        if tipo_relatorio in ['completo', 'compromissos']:
            # Compromissos dos fundos selecionados
            compromissos_filtrados = [c for c in COMPROMISSOS_DATA if c["fundo_id"] in fundo_ids]
            relatorio["dados"]["compromissos"] = compromissos_filtrados
            relatorio["dados"]["total_compromissos"] = sum([c["valor"] for c in compromissos_filtrados])
        
        if tipo_relatorio in ['completo', 'recebimentos']:
            # Recebimentos dos fundos selecionados
            recebimentos_filtrados = [r for r in RECEBIMENTOS_DATA if r["fundo_id"] in fundo_ids]
            relatorio["dados"]["recebimentos"] = recebimentos_filtrados
            relatorio["dados"]["total_recebimentos"] = sum([r["valor"] for r in recebimentos_filtrados])
        
        if tipo_relatorio in ['completo', 'subscricoes']:
            # Subscrições dos fundos selecionados
            subscricoes_filtradas = [s for s in SUBSCRICOES_DATA if s["fundo_id"] in fundo_ids]
            relatorio["dados"]["subscricoes"] = subscricoes_filtradas
            relatorio["dados"]["total_subscricoes"] = sum([s["valor_parcela"] for s in subscricoes_filtradas])
        
        return jsonify({
            "success": True,
            "message": "Relatório gerado com sucesso!",
            "data": relatorio
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tomate_fund_bp.route('/relatorios/templates', methods=['GET'])
def get_templates_relatorio():
    """Obter templates de relatórios disponíveis"""
    templates = [
        {
            "id": "completo",
            "nome": "Relatório Completo",
            "descricao": "Inclui todos os dados: fundos, compromissos, recebimentos e subscrições"
        },
        {
            "id": "fundos",
            "nome": "Relatório de Fundos",
            "descricao": "Apenas dados dos fundos e estatísticas"
        },
        {
            "id": "compromissos",
            "nome": "Relatório de Compromissos",
            "descricao": "Apenas compromissos de pagamento"
        },
        {
            "id": "recebimentos",
            "nome": "Relatório de Recebimentos",
            "descricao": "Apenas recebimentos esperados"
        },
        {
            "id": "subscricoes",
            "nome": "Relatório de Subscrições",
            "descricao": "Apenas subscrições de cotistas"
        }
    ]
    
    return jsonify({
        "success": True,
        "data": templates
    })

# --- ROTAS DE CONSULTA (MANTIDAS) ---

@tomate_fund_bp.route('/dashboard/<fundo_id>', methods=['GET'])
def get_dashboard(fundo_id):
    """Dashboard de tesouraria para um fundo específico"""
    if fundo_id not in FUNDOS_DATA:
        return jsonify({"success": False, "error": "Fundo não encontrado"}), 404
    
    fundo = FUNDOS_DATA[fundo_id]
    hoje = datetime.now()
    
    # Calcular projeções
    periodos = [1, 3, 7, 15, 30]
    projecoes = []
    
    for dias in periodos:
        data_limite = hoje + timedelta(days=dias)
        
        entradas = sum([r["valor"] for r in RECEBIMENTOS_DATA 
                       if r["fundo_id"] == fundo_id and 
                       datetime.strptime(r["vencimento"], "%Y-%m-%d") <= data_limite])
        
        saidas = sum([c["valor"] for c in COMPROMISSOS_DATA 
                     if c["fundo_id"] == fundo_id and 
                     datetime.strptime(c["vencimento"], "%Y-%m-%d") <= data_limite])
        
        saldo_projetado = fundo["liquidez"] + entradas - saidas
        
        projecoes.append({
            "periodo": f"{dias} dias",
            "entradas": entradas,
            "saidas": saidas,
            "saldo_projetado": saldo_projetado
        })
    
    # Alertas de vencimento
    alertas = []
    for comp in COMPROMISSOS_DATA:
        if comp["fundo_id"] == fundo_id:
            venc = datetime.strptime(comp["vencimento"], "%Y-%m-%d")
            dias = (venc - hoje).days
            if dias <= 3:
                if dias < 0:
                    alertas.append(f"{comp['tipo']}: R$ {comp['valor']:,.2f} - VENCIDO!")
                elif dias == 0:
                    alertas.append(f"{comp['tipo']}: R$ {comp['valor']:,.2f} - VENCE HOJE!")
                else:
                    alertas.append(f"{comp['tipo']}: R$ {comp['valor']:,.2f} - {dias} dias")
    
    return jsonify({
        "success": True,
        "data": {
            "fundo": fundo,
            "projecoes": projecoes,
            "alertas": alertas,
            "data_atualizacao": hoje.strftime("%d/%m/%Y %H:%M")
        }
    })

@tomate_fund_bp.route('/compromissos', methods=['GET'])
def get_compromissos():
    """Listar compromissos de pagamento"""
    fundo_id = request.args.get('fundo_id')
    
    compromissos = COMPROMISSOS_DATA
    if fundo_id:
        compromissos = [c for c in compromissos if c["fundo_id"] == fundo_id]
    
    total = sum([c["valor"] for c in compromissos])
    
    return jsonify({
        "success": True,
        "data": compromissos,
        "total_valor": total,
        "total_itens": len(compromissos)
    })

@tomate_fund_bp.route('/recebimentos', methods=['GET'])
def get_recebimentos():
    """Listar recebimentos esperados"""
    fundo_id = request.args.get('fundo_id')
    
    recebimentos = RECEBIMENTOS_DATA
    if fundo_id:
        recebimentos = [r for r in recebimentos if r["fundo_id"] == fundo_id]
    
    total = sum([r["valor"] for r in recebimentos])
    
    return jsonify({
        "success": True,
        "data": recebimentos,
        "total_valor": total,
        "total_itens": len(recebimentos)
    })

@tomate_fund_bp.route('/subscricoes', methods=['GET'])
def get_subscricoes():
    """Listar subscrições pendentes"""
    fundo_id = request.args.get('fundo_id')
    
    subscricoes = SUBSCRICOES_DATA
    if fundo_id:
        subscricoes = [s for s in subscricoes if s["fundo_id"] == fundo_id]
    
    total = sum([s["valor_parcela"] for s in subscricoes])
    
    return jsonify({
        "success": True,
        "data": subscricoes,
        "total_valor": total,
        "total_itens": len(subscricoes)
    })

@tomate_fund_bp.route('/relatorios', methods=['GET'])
def get_relatorios():
    """Relatórios consolidados (resumo)"""
    # Estatísticas gerais
    total_patrimonio = sum([f["patrimonio"] for f in FUNDOS_DATA.values()])
    total_liquidez = sum([f["liquidez"] for f in FUNDOS_DATA.values()])
    total_compromissos = sum([c["valor"] for c in COMPROMISSOS_DATA])
    total_recebimentos = sum([r["valor"] for r in RECEBIMENTOS_DATA])
    total_subscricoes = sum([s["valor_parcela"] for s in SUBSCRICOES_DATA])
    
    # Relatório por fundo
    relatorio_fundos = []
    for fundo_id, fundo in FUNDOS_DATA.items():
        comp_fundo = sum([c["valor"] for c in COMPROMISSOS_DATA if c["fundo_id"] == fundo_id])
        rec_fundo = sum([r["valor"] for r in RECEBIMENTOS_DATA if r["fundo_id"] == fundo_id])
        sub_fundo = sum([s["valor_parcela"] for s in SUBSCRICOES_DATA if s["fundo_id"] == fundo_id])
        
        relatorio_fundos.append({
            "fundo": fundo,
            "compromissos": comp_fundo,
            "recebimentos": rec_fundo,
            "subscricoes": sub_fundo,
            "saldo_projetado": fundo["liquidez"] + rec_fundo - comp_fundo
        })
    
    return jsonify({
        "success": True,
        "data": {
            "resumo_geral": {
                "total_fundos": len(FUNDOS_DATA),
                "patrimonio_total": total_patrimonio,
                "liquidez_total": total_liquidez,
                "compromissos_pendentes": total_compromissos,
                "recebimentos_pendentes": total_recebimentos,
                "subscricoes_pendentes": total_subscricoes,
                "saldo_liquido_projetado": total_liquidez + total_recebimentos - total_compromissos
            },
            "relatorio_por_fundo": relatorio_fundos
        }
    })

@tomate_fund_bp.route('/outliers', methods=['GET'])
def get_outliers():
    """Análise de outliers"""
    # Análise de compromissos
    valores_compromissos = [c["valor"] for c in COMPROMISSOS_DATA]
    outliers_comp = []
    
    if valores_compromissos:
        media_compromissos = sum(valores_compromissos) / len(valores_compromissos)
        outliers_comp_data = [c for c in COMPROMISSOS_DATA if c["valor"] > media_compromissos * 1.5]
        
        for comp in outliers_comp_data:
            desvio = ((comp["valor"] / media_compromissos) - 1) * 100
            outliers_comp.append({
                "item": comp,
                "desvio_percentual": round(desvio, 1)
            })
    
    # Análise de recebimentos
    valores_recebimentos = [r["valor"] for r in RECEBIMENTOS_DATA]
    outliers_rec = []
    
    if valores_recebimentos:
        media_recebimentos = sum(valores_recebimentos) / len(valores_recebimentos)
        outliers_rec_data = [r for r in RECEBIMENTOS_DATA if r["valor"] > media_recebimentos * 1.5]
        
        for rec in outliers_rec_data:
            desvio = ((rec["valor"] / media_recebimentos) - 1) * 100
            outliers_rec.append({
                "item": rec,
                "desvio_percentual": round(desvio, 1)
            })
    
    return jsonify({
        "success": True,
        "data": {
            "compromissos": {
                "media": sum(valores_compromissos) / len(valores_compromissos) if valores_compromissos else 0,
                "maximo": max(valores_compromissos) if valores_compromissos else 0,
                "minimo": min(valores_compromissos) if valores_compromissos else 0,
                "outliers": outliers_comp
            },
            "recebimentos": {
                "media": sum(valores_recebimentos) / len(valores_recebimentos) if valores_recebimentos else 0,
                "maximo": max(valores_recebimentos) if valores_recebimentos else 0,
                "minimo": min(valores_recebimentos) if valores_recebimentos else 0,
                "outliers": outliers_rec
            }
        }
    })

@tomate_fund_bp.route('/documentos', methods=['POST'])
def cadastrar_documento():
    """Simular cadastro de documento"""
    data = request.get_json()
    
    # Simulação de processamento
    documento_processado = {
        "id": 999,
        "tipo": "Debênture",
        "emissor": "Empresa XYZ S.A.",
        "valor": 1000000.00,
        "vencimento": "2025-03-15",
        "taxa": "CDI + 2,5% a.a.",
        "garantias": "Aval dos sócios",
        "status": "PROCESSADO",
        "data_upload": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    return jsonify({
        "success": True,
        "message": "Documento processado com sucesso!",
        "data": documento_processado
    })

@tomate_fund_bp.route('/health', methods=['GET'])
def health_check():
    """Verificação de saúde da API"""
    return jsonify({
        "success": True,
        "message": "API Tomate Fund funcionando!",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "version": "3.0.0",
        "features": ["CRUD Fundos", "Relatórios Personalizados", "Dashboard", "Análise de Outliers"]
    })

# =========================================================
# 3. APLICAÇÃO FLASK PRINCIPAL
# =========================================================

# HTML/CSS/JS da Interface Web (Front-end)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍅 Sistema Tomate Fund - API v3.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }

        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }

        .card-icon {
            font-size: 2rem;
            margin-right: 15px;
        }

        .card-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #2d3748;
        }

        .card-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4a5568;
            margin-bottom: 10px;
        }

        .card-description {
            color: #718096;
            font-size: 0.9rem;
        }

        .controls {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .controls h3 {
            margin-bottom: 20px;
            color: #2d3748;
        }

        .tab-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 15px;
        }

        .tab-btn {
            background: #f7fafc;
            color: #4a5568;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .tab-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .button-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }

        .btn-danger {
            background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        }

        .select-group, .form-group {
            margin-bottom: 20px;
        }

        .select-group label, .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #2d3748;
        }

        .select-group select, .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            transition: border-color 0.3s ease;
        }

        .select-group select:focus, .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .data-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .data-section h3 {
            margin-bottom: 20px;
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #718096;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .table th,
        .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        .table th {
            background: #f7fafc;
            font-weight: 600;
            color: #2d3748;
        }

        .table tr:hover {
            background: #f7fafc;
        }

        .status-pendente {
            background: #fed7d7;
            color: #c53030;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .status-ativo {
            background: #c6f6d5;
            color: #276749;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .alert {
            background: #fed7d7;
            border: 1px solid #feb2b2;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .success {
            background: #c6f6d5;
            border: 1px solid #9ae6b4;
            color: #276749;
        }

        .info {
            background: #bee3f8;
            border: 1px solid #90cdf4;
            color: #2c5282;
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }

        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }

        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }

        .close:hover {
            color: #000;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .button-group, .tab-buttons {
                flex-direction: column;
            }

            .form-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍅 Sistema Tomate Fund v3.0</h1>
            <p>API de Gestão de Tesouraria com CRUD e Relatórios Personalizados</p>
        </div>

        <!-- Dashboard Cards -->
        <div class="dashboard">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💰</div>
                    <div class="card-title">Patrimônio Total</div>
                </div>
                <div class="card-value" id="patrimonio-total">R$ 0,00</div>
                <div class="card-description">Soma de todos os fundos</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💧</div>
                    <div class="card-title">Liquidez Total</div>
                </div>
                <div class="card-value" id="liquidez-total">R$ 0,00</div>
                <div class="card-description">Disponível para investimento</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💸</div>
                    <div class="card-title">Compromissos</div>
                </div>
                <div class="card-value" id="compromissos-total">R$ 0,00</div>
                <div class="card-description">Pagamentos pendentes</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📈</div>
                    <div class="card-title">Recebimentos</div>
                </div>
                <div class="card-value" id="recebimentos-total">R$ 0,00</div>
                <div class="card-description">Valores a receber</div>
            </div>
        </div>

        <!-- Controls with Tabs -->
        <div class="controls">
            <h3>🎛️ Controles do Sistema</h3>
            
            <!-- Tab Buttons -->
            <div class="tab-buttons">
                <button class="tab-btn active" onclick="mostrarTab('consulta', this)">📊 Consulta</button>
                <button class="tab-btn" onclick="mostrarTab('cadastro', this)">📝 Cadastro</button>
                <button class="tab-btn" onclick="mostrarTab('relatorios', this)">📈 Relatórios</button>
            </div>

            <!-- Tab: Consulta -->
            <div id="tab-consulta" class="tab-content active">
                <div class="select-group">
                    <label for="fundo-select">Selecionar Fundo:</label>
                    <select id="fundo-select">
                        <option value="">Carregando fundos...</option>
                    </select>
                </div>

                <div class="button-group">
                    <button class="btn" onclick="carregarDashboard()">📊 Dashboard</button>
                    <button class="btn" onclick="carregarCompromissos()">💸 Compromissos</button>
                    <button class="btn" onclick="carregarRecebimentos()">💰 Recebimentos</button>
                    <button class="btn" onclick="carregarSubscricoes()">📋 Subscrições</button>
                    <button class="btn btn-secondary" onclick="carregarRelatorios()">📈 Relatórios (Resumo)</button>
                    <button class="btn btn-secondary" onclick="carregarOutliers()">📊 Outliers</button>
                </div>
            </div>

            <!-- Tab: Cadastro -->
            <div id="tab-cadastro" class="tab-content">
                <h4>📝 Gerenciar Fundos</h4>
                
                <div class="button-group">
                    <button class="btn btn-secondary" onclick="mostrarFormularioFundo()">➕ Novo Fundo</button>
                    <button class="btn" onclick="listarFundos()">📋 Listar Fundos</button>
                </div>

                <div id="formulario-fundo" style="display: none;">
                    <h5>Cadastrar Novo Fundo</h5>
                    <form id="form-fundo">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="nome">Nome do Fundo *</label>
                                <input type="text" id="nome" name="nome" required>
                            </div>
                            <div class="form-group">
                                <label for="cnpj">CNPJ *</label>
                                <input type="text" id="cnpj" name="cnpj" required placeholder="00.000.000/0000-00">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="patrimonio">Patrimônio (R$) *</label>
                                <input type="number" id="patrimonio" name="patrimonio" step="0.01" required>
                            </div>
                            <div class="form-group">
                                <label for="liquidez">Liquidez (R$) *</label>
                                <input type="number" id="liquidez" name="liquidez" step="0.01" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="politica_liquidez">Política de Liquidez *</label>
                                <select id="politica_liquidez" name="politica_liquidez" required>
                                    <option value="">Selecione...</option>
                                    <option value="Ativos de Risco">Ativos de Risco</option>
                                    <option value="Livre de Risco">Livre de Risco</option>
                                    <option value="Misto">Misto</option>
                                    <option value="Específico">Específico</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="prazo_resgate">Prazo de Resgate (dias)</label>
                                <input type="number" id="prazo_resgate" name="prazo_resgate" value="30">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="gestor">Gestor *</label>
                                <input type="text" id="gestor" name="gestor" required>
                            </div>
                            <div class="form-group">
                                <label for="taxa_admin">Taxa de Administração (% a.a.) *</label>
                                <input type="number" id="taxa_admin" name="taxa_admin" step="0.01" required>
                            </div>
                        </div>
                        
                        <div class="button-group">
                            <button type="submit" class="btn btn-secondary">💾 Salvar Fundo</button>
                            <button type="button" class="btn" onclick="cancelarFormulario()">❌ Cancelar</button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Tab: Relatórios -->
            <div id="tab-relatorios" class="tab-content">
                <h4>📈 Gerador de Relatórios Personalizados</h4>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="tipo-relatorio">Tipo de Relatório</label>
                        <select id="tipo-relatorio">
                            <option value="completo">Relatório Completo</option>
                            <option value="fundos">Apenas Fundos</option>
                            <option value="compromissos">Apenas Compromissos</option>
                            <option value="recebimentos">Apenas Recebimentos</option>
                            <option value="subscricoes">Apenas Subscrições</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="fundos-relatorio">Fundos (deixe vazio para todos)</label>
                        <select id="fundos-relatorio" multiple>
                            <!-- Preenchido dinamicamente -->
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="data-inicio">Data Início</label>
                        <input type="date" id="data-inicio">
                    </div>
                    <div class="form-group">
                        <label for="data-fim">Data Fim</label>
                        <input type="date" id="data-fim">
                    </div>
                </div>
                
                <div class="button-group">
                    <button class="btn btn-secondary" onclick="gerarRelatorioPersonalizado()">📊 Gerar Relatório</button>
                    <button class="btn" onclick="carregarTemplatesRelatorio()">📋 Ver Templates</button>
                </div>
            </div>
        </div>

        <!-- Data Display -->
        <div class="data-section">
            <h3 id="data-title">📋 Dados do Sistema</h3>
            <div id="data-content">
                <div class="loading">
                    <p>Selecione uma opção acima para visualizar os dados</p>
                </div>
            </div>
        </div>

        <!-- Modal para Edição de Fundos -->
        <div id="modal-editar-fundo" class="modal">
            <div class="modal-content">
                <span class="close" onclick="fecharModal()">&times;</span>
                <h3>✏️ Editar Fundo</h3>
                <form id="form-editar-fundo">
                    <input type="hidden" id="edit-fundo-id">
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="edit-nome">Nome do Fundo</label>
                            <input type="text" id="edit-nome" name="nome" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-cnpj">CNPJ</label>
                            <input type="text" id="edit-cnpj" name="cnpj" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="edit-patrimonio">Patrimônio (R$)</label>
                            <input type="number" id="edit-patrimonio" name="patrimonio" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-liquidez">Liquidez (R$)</label>
                            <input type="number" id="edit-liquidez" name="liquidez" step="0.01" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="edit-politica_liquidez">Política de Liquidez</label>
                            <select id="edit-politica_liquidez" name="politica_liquidez" required>
                                <option value="Ativos de Risco">Ativos de Risco</option>
                                <option value="Livre de Risco">Livre de Risco</option>
                                <option value="Misto">Misto</option>
                                <option value="Específico">Específico</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="edit-prazo_resgate">Prazo de Resgate (dias)</label>
                            <input type="number" id="edit-prazo_resgate" name="prazo_resgate">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="edit-gestor">Gestor</label>
                            <input type="text" id="edit-gestor" name="gestor" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-taxa_admin">Taxa de Administração (% a.a.)</label>
                            <input type="number" id="edit-taxa_admin" name="taxa_admin" step="0.01" required>
                        </div>
                    </div>
                    
                    <div class="button-group">
                        <button type="submit" class="btn btn-secondary">💾 Salvar Alterações</button>
                        <button type="button" class="btn" onclick="fecharModal()">❌ Cancelar</button>
                    </div>
                </form>
            </div>
        </div>

        <div class="footer">
            <p>🍅 Sistema Tomate Fund v3.0 | API REST com CRUD e Relatórios Personalizados</p>
        </div>
    </div>

    <script>
        // Configuração da API
        const API_BASE = '/api';
        let fundoAtual = '';

        // Formatador de moeda
        function formatarMoeda(valor) {
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            }).format(valor);
        }

        // Fazer requisição para API
        async function fazerRequisicao(endpoint, options = {}) {
            try {
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Erro na requisição:', error);
                return { success: false, error: 'Erro de conexão' };
            }
        }

        // Gerenciar tabs
        function mostrarTab(tabName, element) {
            // Esconder todas as tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            // Mostrar tab selecionada
            document.getElementById(`tab-${tabName}`).classList.add('active');
            element.classList.add('active');

            // Carregar dados específicos da tab
            if (tabName === 'relatorios') {
                carregarFundosParaRelatorio();
            }
            if (tabName === 'cadastro') {
                listarFundos();
            }
        }

        // Carregar fundos no select
        async function carregarFundos() {
            const result = await fazerRequisicao('/fundos');
            if (result.success) {
                const select = document.getElementById('fundo-select');
                select.innerHTML = '<option value="">Todos os fundos</option>';
                
                result.data.forEach(fundo => {
                    const option = document.createElement('option');
                    option.value = fundo.id;
                    option.textContent = fundo.nome;
                    if (fundo.id === fundoAtual) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                });

                select.addEventListener('change', (e) => {
                    fundoAtual = e.target.value;
                    carregarResumoGeral();
                });
                
                // Selecionar o primeiro fundo se nenhum estiver selecionado
                if (!fundoAtual && result.data.length > 0) {
                    fundoAtual = result.data[0].id;
                    select.value = fundoAtual;
                }
            }
        }

        // Carregar fundos para relatório
        async function carregarFundosParaRelatorio() {
            const result = await fazerRequisicao('/fundos');
            if (result.success) {
                const select = document.getElementById('fundos-relatorio');
                select.innerHTML = '';
                
                result.data.forEach(fundo => {
                    const option = document.createElement('option');
                    option.value = fundo.id;
                    option.textContent = fundo.nome;
                    select.appendChild(option);
                });
            }
        }

        // Carregar resumo geral
        async function carregarResumoGeral() {
            const result = await fazerRequisicao('/relatorios');
            if (result.success) {
                const resumo = result.data.resumo_geral;
                document.getElementById('patrimonio-total').textContent = formatarMoeda(resumo.patrimonio_total);
                document.getElementById('liquidez-total').textContent = formatarMoeda(resumo.liquidez_total);
                document.getElementById('compromissos-total').textContent = formatarMoeda(resumo.compromissos_pendentes);
                document.getElementById('recebimentos-total').textContent = formatarMoeda(resumo.recebimentos_pendentes);
            }
        }

        // Mostrar formulário de fundo
        function mostrarFormularioFundo() {
            document.getElementById('formulario-fundo').style.display = 'block';
            document.getElementById('form-fundo').reset();
        }

        // Cancelar formulário
        function cancelarFormulario() {
            document.getElementById('formulario-fundo').style.display = 'none';
        }

        // Listar fundos para gerenciamento
        async function listarFundos() {
            const result = await fazerRequisicao('/fundos');
            if (result.success) {
                let html = `
                    <div class="alert info">
                        <strong>Total de Fundos:</strong> ${result.total} fundos cadastrados
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nome</th>
                                <th>CNPJ</th>
                                <th>Patrimônio</th>
                                <th>Status</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                result.data.forEach(fundo => {
                    html += `
                        <tr>
                            <td>${fundo.id}</td>
                            <td>${fundo.nome}</td>
                            <td>${fundo.cnpj}</td>
                            <td>${formatarMoeda(fundo.patrimonio)}</td>
                            <td><span class="status-ativo">${fundo.status}</span></td>
                            <td>
                                <button class="btn" onclick="editarFundo('${fundo.id}')" style="padding: 5px 10px; margin-right: 5px;">✏️</button>
                                <button class="btn btn-danger" onclick="deletarFundo('${fundo.id}', '${fundo.nome}')" style="padding: 5px 10px;">🗑️</button>
                            </td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                mostrarDados('📋 Gerenciar Fundos', html);
            }
        }

        // Editar fundo
        async function editarFundo(fundoId) {
            const result = await fazerRequisicao(`/fundos/${fundoId}`);
            if (result.success) {
                const fundo = result.data;
                
                // Preencher formulário de edição
                document.getElementById('edit-fundo-id').value = fundo.id;
                document.getElementById('edit-nome').value = fundo.nome;
                document.getElementById('edit-cnpj').value = fundo.cnpj;
                document.getElementById('edit-patrimonio').value = fundo.patrimonio;
                document.getElementById('edit-liquidez').value = fundo.liquidez;
                document.getElementById('edit-politica_liquidez').value = fundo.politica_liquidez;
                document.getElementById('edit-prazo_resgate').value = fundo.prazo_resgate;
                document.getElementById('edit-gestor').value = fundo.gestor;
                document.getElementById('edit-taxa_admin').value = fundo.taxa_admin;
                
                // Mostrar modal
                document.getElementById('modal-editar-fundo').style.display = 'block';
            }
        }

        // Deletar fundo
        async function deletarFundo(fundoId, nomeFundo) {
            if (confirm(`Tem certeza que deseja deletar o fundo "${nomeFundo}"?\n\nEsta ação não pode ser desfeita e removerá todos os dados relacionados.`)) {
                const result = await fazerRequisicao(`/fundos/${fundoId}`, {
                    method: 'DELETE'
                });
                
                if (result.success) {
                    mostrarSucesso(result.message);
                    listarFundos(); // Recarregar lista
                    carregarFundos(); // Recarregar select
                    carregarResumoGeral(); // Atualizar dashboard
                } else {
                    mostrarErro(result.error);
                }
            }
        }

        // Fechar modal
        function fecharModal() {
            document.getElementById('modal-editar-fundo').style.display = 'none';
        }

        // Gerar relatório personalizado
        async function gerarRelatorioPersonalizado() {
            const tipo = document.getElementById('tipo-relatorio').value;
            const fundosSelect = document.getElementById('fundos-relatorio');
            const fundosSelecionados = Array.from(fundosSelect.selectedOptions).map(option => option.value);
            const dataInicio = document.getElementById('data-inicio').value;
            const dataFim = document.getElementById('data-fim').value;

            const dados = {
                tipo: tipo,
                fundos: fundosSelecionados.length > 0 ? fundosSelecionados : undefined,
                data_inicio: dataInicio || undefined,
                data_fim: dataFim || undefined
            };

            const result = await fazerRequisicao('/relatorios/gerar', {
                method: 'POST',
                body: JSON.stringify(dados)
            });

            if (result.success) {
                const relatorio = result.data;
                let html = `
                    <div class="alert success">
                        <strong>Relatório Gerado:</strong> ${relatorio.tipo}<br>
                        <strong>Data:</strong> ${relatorio.data_geracao}<br>
                        <strong>Fundos Analisados:</strong> ${relatorio.fundos_analisados}
                    </div>
                `;

                if (relatorio.dados.fundos) {
                    html += '<h4>📊 Fundos</h4>';
                    html += '<table class="table"><thead><tr><th>Nome</th><th>Patrimônio</th><th>Liquidez</th><th>Gestor</th></tr></thead><tbody>';
                    relatorio.dados.fundos.forEach(fundo => {
                        html += `<tr><td>${fundo.nome}</td><td>${formatarMoeda(fundo.patrimonio)}</td><td>${formatarMoeda(fundo.liquidez)}</td><td>${fundo.gestor}</td></tr>`;
                    });
                    html += '</tbody></table>';

                    if (relatorio.dados.estatisticas_fundos) {
                        const stats = relatorio.dados.estatisticas_fundos;
                        html += `
                            <h5>📈 Estatísticas</h5>
                            <p><strong>Patrimônio Total:</strong> ${formatarMoeda(stats.total_patrimonio)}</p>
                            <p><strong>Liquidez Total:</strong> ${formatarMoeda(stats.total_liquidez)}</p>
                            <p><strong>Patrimônio Médio:</strong> ${formatarMoeda(stats.patrimonio_medio)}</p>
                            <p><strong>Liquidez Média:</strong> ${formatarMoeda(stats.liquidez_media)}</p>
                        `;
                    }
                }

                if (relatorio.dados.compromissos) {
                    html += `<h4>💸 Compromissos (Total: ${formatarMoeda(relatorio.dados.total_compromissos)})</h4>`;
                    html += '<table class="table"><thead><tr><th>Tipo</th><th>Valor</th><th>Vencimento</th></tr></thead><tbody>';
                    relatorio.dados.compromissos.forEach(comp => {
                        html += `<tr><td>${comp.tipo}</td><td>${formatarMoeda(comp.valor)}</td><td>${comp.vencimento}</td></tr>`;
                    });
                    html += '</tbody></table>';
                }

                if (relatorio.dados.recebimentos) {
                    html += `<h4>💰 Recebimentos (Total: ${formatarMoeda(relatorio.dados.total_recebimentos)})</h4>`;
                    html += '<table class="table"><thead><tr><th>Tipo</th><th>Valor</th><th>Vencimento</th></tr></thead><tbody>';
                    relatorio.dados.recebimentos.forEach(rec => {
                        html += `<tr><td>${rec.tipo}</td><td>${formatarMoeda(rec.valor)}</td><td>${rec.vencimento}</td></tr>`;
                    });
                    html += '</tbody></table>';
                }

                if (relatorio.dados.subscricoes) {
                    html += `<h4>📋 Subscrições (Total: ${formatarMoeda(relatorio.dados.total_subscricoes)})</h4>`;
                    html += '<table class="table"><thead><tr><th>Cotista</th><th>Valor</th><th>Vencimento</th></tr></thead><tbody>';
                    relatorio.dados.subscricoes.forEach(sub => {
                        html += `<tr><td>${sub.cotista}</td><td>${formatarMoeda(sub.valor_parcela)}</td><td>${sub.vencimento}</td></tr>`;
                    });
                    html += '</tbody></table>';
                }

                mostrarDados('📊 Relatório Personalizado', html);
            } else {
                mostrarErro(result.error);
            }
        }

        // Carregar templates de relatório
        async function carregarTemplatesRelatorio() {
            const result = await fazerRequisicao('/relatorios/templates');
            if (result.success) {
                let html = '<h4>📋 Templates de Relatórios Disponíveis</h4>';
                result.data.forEach(template => {
                    html += `
                        <div style="margin-bottom: 15px; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px;">
                            <h5>${template.nome}</h5>
                            <p>${template.descricao}</p>
                            <button class="btn" onclick="selecionarTemplate('${template.id}')" style="margin-top: 10px;">Usar Template</button>
                        </div>
                    `;
                });
                mostrarDados('📋 Templates de Relatórios', html);
            }
        }

        // Selecionar template
        function selecionarTemplate(templateId) {
            document.getElementById('tipo-relatorio').value = templateId;
            mostrarTab('relatorios', document.querySelector('.tab-btn:nth-child(3)'));
        }

        // Event Listeners para formulários
        document.getElementById('form-fundo').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const dados = Object.fromEntries(formData.entries());
            
            const result = await fazerRequisicao('/fundos', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
            
            if (result.success) {
                mostrarSucesso(result.message);
                cancelarFormulario();
                carregarFundos();
                carregarResumoGeral();
                listarFundos();
            } else {
                mostrarErro(result.error);
            }
        });

        document.getElementById('form-editar-fundo').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fundoId = document.getElementById('edit-fundo-id').value;
            const formData = new FormData(e.target);
            const dados = Object.fromEntries(formData.entries());
            delete dados.id; // Remover ID dos dados
            
            const result = await fazerRequisicao(`/fundos/${fundoId}`, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
            
            if (result.success) {
                mostrarSucesso(result.message);
                fecharModal();
                listarFundos();
                carregarFundos();
                carregarResumoGeral();
            } else {
                mostrarErro(result.error);
            }
        });

        // Funções existentes (mantidas)
        async function carregarDashboard() {
            if (!fundoAtual) {
                mostrarErro('Selecione um fundo específico para ver o dashboard');
                return;
            }

            const result = await fazerRequisicao(`/dashboard/${fundoAtual}`);
            if (result.success) {
                const data = result.data;
                let html = `
                    <div class="alert success">
                        <strong>Dashboard do ${data.fundo.nome}</strong><br>
                        Atualizado em: ${data.data_atualizacao}
                    </div>
                    
                    <h4>📊 Informações do Fundo</h4>
                    <table class="table">
                        <tr><td><strong>CNPJ:</strong></td><td>${data.fundo.cnpj}</td></tr>
                        <tr><td><strong>Gestor:</strong></td><td>${data.fundo.gestor}</td></tr>
                        <tr><td><strong>Patrimônio:</strong></td><td>${formatarMoeda(data.fundo.patrimonio)}</td></tr>
                        <tr><td><strong>Liquidez:</strong></td><td>${formatarMoeda(data.fundo.liquidez)}</td></tr>
                        <tr><td><strong>Política:</strong></td><td>${data.fundo.politica_liquidez}</td></tr>
                        <tr><td><strong>Taxa Admin:</strong></td><td>${data.fundo.taxa_admin}% a.a.</td></tr>
                    </table>

                    <h4>💰 Projeções de Fluxo de Caixa</h4>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Período</th>
                                <th>Entradas</th>
                                <th>Saídas</th>
                                <th>Saldo Projetado</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.projecoes.forEach(proj => {
                    html += `
                        <tr>
                            <td>${proj.periodo}</td>
                            <td>${formatarMoeda(proj.entradas)}</td>
                            <td>${formatarMoeda(proj.saidas)}</td>
                            <td>${formatarMoeda(proj.saldo_projetado)}</td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';

                if (data.alertas.length > 0) {
                    html += '<h4>🚨 Alertas Importantes</h4><div class="alert">';
                    data.alertas.forEach(alerta => {
                        html += `<p>• ${alerta}</p>`;
                    });
                    html += '</div>';
                }

                mostrarDados('📊 Dashboard de Tesouraria', html);
            }
        }

        async function carregarCompromissos() {
            const endpoint = fundoAtual ? `/compromissos?fundo_id=${fundoAtual}` : '/compromissos';
            const result = await fazerRequisicao(endpoint);
            
            if (result.success) {
                let html = `
                    <div class="alert success">
                        <strong>Total de Compromissos:</strong> ${formatarMoeda(result.total_valor)} 
                        (${result.total_itens} itens)
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tipo</th>
                                <th>Valor</th>
                                <th>Vencimento</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                result.data.forEach(comp => {
                    html += `
                        <tr>
                            <td>${comp.id}</td>
                            <td>${comp.tipo}</td>
                            <td>${formatarMoeda(comp.valor)}</td>
                            <td>${comp.vencimento}</td>
                            <td><span class="status-pendente">${comp.status}</span></td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                mostrarDados('💸 Compromissos de Pagamento', html);
            }
        }

        async function carregarRecebimentos() {
            const endpoint = fundoAtual ? `/recebimentos?fundo_id=${fundoAtual}` : '/recebimentos';
            const result = await fazerRequisicao(endpoint);
            
            if (result.success) {
                let html = `
                    <div class="alert success">
                        <strong>Total de Recebimentos:</strong> ${formatarMoeda(result.total_valor)} 
                        (${result.total_itens} itens)
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tipo</th>
                                <th>Valor</th>
                                <th>Vencimento</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                result.data.forEach(rec => {
                    html += `
                        <tr>
                            <td>${rec.id}</td>
                            <td>${rec.tipo}</td>
                            <td>${formatarMoeda(rec.valor)}</td>
                            <td>${rec.vencimento}</td>
                            <td><span class="status-pendente">${rec.status}</span></td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                mostrarDados('💰 Recebimentos Esperados', html);
            }
        }

        async function carregarSubscricoes() {
            const endpoint = fundoAtual ? `/subscricoes?fundo_id=${fundoAtual}` : '/subscricoes';
            const result = await fazerRequisicao(endpoint);
            
            if (result.success) {
                let html = `
                    <div class="alert success">
                        <strong>Total de Subscrições:</strong> ${formatarMoeda(result.total_valor)} 
                        (${result.total_itens} itens)
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Cotista</th>
                                <th>CPF/CNPJ</th>
                                <th>Cotas</th>
                                <th>Valor</th>
                                <th>Vencimento</th>
                                <th>Parcela</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                result.data.forEach(sub => {
                    html += `
                        <tr>
                            <td>${sub.id}</td>
                            <td>${sub.cotista}</td>
                            <td>${sub.cpf_cnpj}</td>
                            <td>${sub.cotas}</td>
                            <td>${formatarMoeda(sub.valor_parcela)}</td>
                            <td>${sub.vencimento}</td>
                            <td>${sub.parcela}</td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                mostrarDados('📋 Subscrições Pendentes', html);
            }
        }

        async function carregarOutliers() {
            const result = await fazerRequisicao('/outliers');
            
            if (result.success) {
                const data = result.data;
                let html = `
                    <h4>💸 Análise de Compromissos</h4>
                    <table class="table">
                        <tr><td><strong>Média:</strong></td><td>${formatarMoeda(data.compromissos.media)}</td></tr>
                        <tr><td><strong>Máximo:</strong></td><td>${formatarMoeda(data.compromissos.maximo)}</td></tr>
                        <tr><td><strong>Mínimo:</strong></td><td>${formatarMoeda(data.compromissos.minimo)}</td></tr>
                    </table>
                `;

                if (data.compromissos.outliers.length > 0) {
                    html += '<h5>🔴 Outliers de Compromissos</h5>';
                    data.compromissos.outliers.forEach(outlier => {
                        html += `<p>• ${outlier.item.tipo}: ${formatarMoeda(outlier.item.valor)} (+${outlier.desvio_percentual}% da média)</p>`;
                    });
                } else {
                    html += '<p>✅ Nenhum outlier encontrado em compromissos</p>';
                }

                html += `
                    <h4>💰 Análise de Recebimentos</h4>
                    <table class="table">
                        <tr><td><strong>Média:</strong></td><td>${formatarMoeda(data.recebimentos.media)}</td></tr>
                        <tr><td><strong>Máximo:</strong></td><td>${formatarMoeda(data.recebimentos.maximo)}</td></tr>
                        <tr><td><strong>Mínimo:</strong></td><td>${formatarMoeda(data.recebimentos.minimo)}</td></tr>
                    </table>
                `;

                if (data.recebimentos.outliers.length > 0) {
                    html += '<h5>🟡 Outliers de Recebimentos</h5>';
                    data.recebimentos.outliers.forEach(outlier => {
                        html += `<p>• ${outlier.item.tipo}: ${formatarMoeda(outlier.item.valor)} (+${outlier.desvio_percentual}% da média)</p>`;
                    });
                } else {
                    html += '<p>✅ Nenhum outlier encontrado em recebimentos</p>';
                }

                mostrarDados('📊 Análise de Outliers', html);
            }
        }

        // Mostrar dados na tela
        function mostrarDados(titulo, html) {
            document.getElementById('data-title').textContent = titulo;
            document.getElementById('data-content').innerHTML = html;
        }

        // Mostrar erro
        function mostrarErro(mensagem) {
            const html = `<div class="alert">${mensagem}</div>`;
            mostrarDados('❌ Erro', html);
        }

        // Mostrar sucesso
        function mostrarSucesso(mensagem) {
            const html = `<div class="alert success">${mensagem}</div>`;
            mostrarDados('✅ Sucesso', html);
        }

        // Fechar modal ao clicar fora
        window.onclick = function(event) {
            const modal = document.getElementById('modal-editar-fundo');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        // Inicializar aplicação
        document.addEventListener('DOMContentLoaded', function() {
            carregarFundos();
            carregarResumoGeral();
        });
    </script>
</body>
</html>
"""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tomate_fund_secret_key_2024'

# Habilitar CORS para todas as rotas
CORS(app)

app.register_blueprint(tomate_fund_bp, url_prefix='/api')

@app.route('/')
def serve_index():
    """Serve a página HTML principal"""
    return HTML_CONTENT
  if __name__ == '__main__':
    print("=========================================================")
    print("🍅 SISTEMA TOMATE FUND - API + FRONT-END (v3.0) 🍅")
    print("=========================================================")
    print("Acesse no navegador: http://localhost:5000")
    print("=========================================================")
    app.run(host='0.0.0.0', port=5000)

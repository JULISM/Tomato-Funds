
import os

def update_main():
    path = '/home/ubuntu/upload/main.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Adicionar rota para cadastrar ativos no Flask
    # Vamos inserir antes da rota /documentos
    new_route = """
@app.route('/ativos', methods=['POST'])
def cadastrar_ativo():
    \"\"\"Cadastrar um novo ativo\"\"\"
    try:
        # No caso de upload de arquivo, usamos request.form e request.files
        data = request.form
        arquivo = request.files.get('documento')
        
        novo_ativo = {
            "id": str(uuid.uuid4())[:8],
            "tipo_ativo": data.get('tipo_ativo'),
            "detalhes": data.get('detalhes'),
            "taxa_fixa": data.get('taxa_fixa'),
            "taxa_variavel": data.get('taxa_variavel'),
            "vencimentos": data.getlist('vencimentos[]'),
            "info_gerais": data.get('info_gerais'),
            "arquivo_nome": arquivo.filename if arquivo else "Nenhum arquivo",
            "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Aqui você poderia salvar no banco de dados
        print(f"Ativo cadastrado: {novo_ativo}")
        
        return jsonify({
            "success": True,
            "message": "Ativo cadastrado com sucesso!",
            "data": novo_ativo
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
"""
    content = content.replace("@app.route('/documentos', methods=['POST'])", new_route + "\n@app.route('/documentos', methods=['POST'])")

    # 2. Atualizar o HTML: Botão de Cadastro Ativo e novo formulário
    # Substituir o botão antigo
    old_btn = '<button class="btn btn-secondary" onclick="mostrarSucesso(\'Funcionalidade Cadastro Ativo em desenvolvimento\')">✅ Cadastro Ativo</button>'
    new_btn = '<button class="btn btn-secondary" onclick="mostrarFormularioAtivo()">✅ Cadastro Ativo</button>'
    content = content.replace(old_btn, new_btn)

    # Inserir o novo formulário de ativos após o formulário de fundo
    new_form_html = """
                <div id="formulario-ativo" style="display: none; margin-top: 20px; border-top: 2px solid #e2e8f0; padding-top: 20px;">
                    <h5>Cadastrar Novo Ativo</h5>
                    <form id="form-ativo" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="tipo_ativo">Tipo do Ativo *</label>
                            <select id="tipo_ativo" name="tipo_ativo" required>
                                <option value="">Selecione o tipo de ativo...</option>
                                <option value="Ações de companhias fechadas">Ações de companhias fechadas</option>
                                <option value="Quotas de sociedades limitadas">Quotas de sociedades limitadas</option>
                                <option value="Debêntures (inclusive conversíveis)">Debêntures (inclusive conversíveis)</option>
                                <option value="Notas comerciais">Notas comerciais</option>
                                <option value="Cédulas de Crédito Bancário (CCB)">Cédulas de Crédito Bancário (CCB)</option>
                                <option value="Cédulas de Crédito Imobiliário (CCI)">Cédulas de Crédito Imobiliário (CCI)</option>
                                <option value="Certificados de Recebíveis Imobiliários (CRI)">Certificados de Recebíveis Imobiliários (CRI)</option>
                                <option value="Certificados de Recebíveis do Agronegócio (CRA)">Certificados de Recebíveis do Agronegócio (CRA)</option>
                                <option value="Direitos creditórios Recebíveis comerciais">Direitos creditórios Recebíveis comerciais</option>
                                <option value="Recebíveis financeiros">Recebíveis financeiros</option>
                                <option value="Créditos inadimplentes (NPL)">Créditos inadimplentes (NPL)</option>
                                <option value="Créditos judiciais">Créditos judiciais</option>
                                <option value="Precatórios">Precatórios</option>
                                <option value="Imóveis">Imóveis</option>
                                <option value="Terrenos">Terrenos</option>
                                <option value="Direitos reais sobre imóveis">Direitos reais sobre imóveis</option>
                                <option value="Participações em SPE">Participações em SPE</option>
                                <option value="Projetos de infraestrutura">Projetos de infraestrutura</option>
                                <option value="Concessões">Concessões</option>
                                <option value="Parcerias Público-Privadas (PPP)">Parcerias Público-Privadas (PPP)</option>
                                <option value="Royalties">Royalties</option>
                                <option value="Direitos econômicos">Direitos econômicos</option>
                                <option value="Créditos de carbono">Créditos de carbono</option>
                                <option value="Quotas de FIP">Quotas de FIP</option>
                                <option value="Quotas de FII">Quotas de FII</option>
                                <option value="Quotas de FIDC">Quotas de FIDC</option>
                                <option value="Green Bonds">Green Bonds</option>
                                <option value="Floating Rate Notes (FRN)">Floating Rate Notes (FRN)</option>
                                <option value="Fixed Rate Bonds">Fixed Rate Bonds</option>
                                <option value="Portuguese Government Bonds (Portugal)">Portuguese Government Bonds (Portugal)</option>
                                <option value="Gilts (Reino Unido)">Gilts (Reino Unido)</option>
                                <option value="OATs (França)">OATs (França)</option>
                                <option value="Corporate Bonds Fixed rate">Corporate Bonds Fixed rate</option>
                                <option value="Corporate Bonds Floating rates">Corporate Bonds Floating rates</option>
                                <option value="TIPS – Treasury Inflation-Protected Securities">TIPS – Treasury Inflation-Protected Securities</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="detalhes">Detalhes do Ativo</label>
                            <textarea id="detalhes" name="detalhes" rows="3" placeholder="Descreva os detalhes do ativo..."></textarea>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="taxa_fixa">Remuneração - Taxa Fixa (%)</label>
                                <input type="number" id="taxa_fixa" name="taxa_fixa" step="0.0001" placeholder="Ex: 12.5">
                            </div>
                            <div class="form-group">
                                <label for="taxa_variavel">Remuneração - Taxa Variável</label>
                                <select id="taxa_variavel" name="taxa_variavel">
                                    <option value="">Nenhuma</option>
                                    <option value="CDI">CDI</option>
                                    <option value="Selic">Selic</option>
                                    <option value="Cambial">Cambial</option>
                                    <option value="IPCA">IPCA</option>
                                    <option value="IGPM">IGPM</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Vencimentos</label>
                            <div id="vencimentos-container">
                                <div class="form-row" style="margin-bottom: 10px;">
                                    <input type="date" name="vencimentos[]" class="vencimento-input">
                                    <button type="button" class="btn btn-secondary" onclick="adicionarDataVencimento()" style="padding: 5px 15px;">+</button>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="info_gerais">Informações Gerais (máx. 1000 caracteres)</label>
                            <textarea id="info_gerais" name="info_gerais" rows="5" maxlength="1000" placeholder="Informações adicionais..."></textarea>
                        </div>

                        <div class="form-group">
                            <label for="documento">Upload do Documento</label>
                            <input type="file" id="documento" name="documento" class="btn" style="background: #f7fafc; color: #4a5568; border: 2px dashed #e2e8f0; width: 100%;">
                        </div>

                        <div class="button-group">
                            <button type="submit" class="btn btn-secondary">💾 Salvar Ativo</button>
                            <button type="button" class="btn" onclick="cancelarFormularioAtivo()">❌ Cancelar</button>
                        </div>
                    </form>
                </div>
"""
    content = content.replace('</form>\n                </div>\n            </div>', '</form>\n                </div>\n' + new_form_html + '\n            </div>')

    # 3. Adicionar as funções JavaScript necessárias
    new_js_functions = """
        function mostrarFormularioAtivo() {
            document.getElementById('formulario-fundo').style.display = 'none';
            document.getElementById('formulario-ativo').style.display = 'block';
        }

        function cancelarFormularioAtivo() {
            document.getElementById('formulario-ativo').style.display = 'none';
            document.getElementById('form-ativo').reset();
            // Limpar datas extras de vencimento
            const container = document.getElementById('vencimentos-container');
            container.innerHTML = `
                <div class="form-row" style="margin-bottom: 10px;">
                    <input type="date" name="vencimentos[]" class="vencimento-input">
                    <button type="button" class="btn btn-secondary" onclick="adicionarDataVencimento()" style="padding: 5px 15px;">+</button>
                </div>
            `;
        }

        function adicionarDataVencimento() {
            const container = document.getElementById('vencimentos-container');
            const div = document.createElement('div');
            div.className = 'form-row';
            div.style.marginBottom = '10px';
            div.innerHTML = `
                <input type="date" name="vencimentos[]" class="vencimento-input">
                <button type="button" class="btn btn-danger" onclick="this.parentElement.remove()" style="padding: 5px 15px;">-</button>
            `;
            container.appendChild(div);
        }

        // Listener para o formulário de ativos
        document.addEventListener('DOMContentLoaded', function() {
            const formAtivo = document.getElementById('form-ativo');
            if (formAtivo) {
                formAtivo.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(this);
                    
                    try {
                        const response = await fetch('/ativos', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        
                        if (result.success) {
                            mostrarSucesso(result.message);
                            cancelarFormularioAtivo();
                        } else {
                            mostrarErro(result.error);
                        }
                    } catch (error) {
                        mostrarErro('Erro ao conectar com o servidor');
                    }
                });
            }
        });
"""
    # Inserir antes do fechamento da tag script
    content = content.replace('</script>', new_js_functions + '\n    </script>')

    # Salvar o arquivo atualizado
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Arquivo main.py atualizado com sucesso!")

if __name__ == "__main__":
    update_main()

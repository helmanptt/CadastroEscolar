from flask import Blueprint, request, jsonify
from database import mysql
import MySQLdb

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

@alunos_bp.route('/novoaluno', methods=['POST'])
def novo_aluno():
    """Cadastrar novo aluno"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        nome = data.get('nome')
        email = data.get('email')

        if not nome or not email:
            return jsonify({'erro': 'Nome e email são obrigatórios'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO alunos (nome, email) VALUES (%s, %s)", (nome, email))
        mysql.connection.commit()
        
        aluno_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'mensagem': 'Aluno cadastrado com sucesso',
            'aluno': {
                'id': aluno_id,
                'nome': nome,
                'email': email
            }
        }), 201
        
    except MySQLdb.IntegrityError as e:
        mysql.connection.rollback()
        if 'Duplicate entry' in str(e):
            return jsonify({'erro': 'Este email já está cadastrado'}), 400
        return jsonify({'erro': 'Erro de integridade no banco de dados'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@alunos_bp.route('', methods=['GET'])
def listar_alunos():
    """Listar todos os alunos"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nome, email FROM alunos ORDER BY nome")
        alunos = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'alunos': [
                {
                    'id': aluno[0], 
                    'nome': aluno[1], 
                    'email': aluno[2]
                } for aluno in alunos
            ],
            'total': len(alunos)
        })
    except Exception as e:
        return jsonify({'erro': f'Erro ao listar alunos: {str(e)}'}), 500

@alunos_bp.route('/<int:id>', methods=['GET'])
def detalhes_aluno(id):
    """Ver detalhes de um aluno"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nome, email FROM alunos WHERE id = %s", (id,))
        aluno = cursor.fetchone()
        cursor.close()
        
        if aluno:
            return jsonify({
                'aluno': {
                    'id': aluno[0], 
                    'nome': aluno[1], 
                    'email': aluno[2]
                }
            })
        return jsonify({'erro': 'Aluno não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar aluno: {str(e)}'}), 500

@alunos_bp.route('/atualizaaluno', methods=['PUT'])
def atualizar_aluno():
    """Atualizar dados de um aluno"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        id_aluno = data.get('id')
        nome = data.get('nome')
        email = data.get('email')
        
        if not id_aluno or not nome or not email:
            return jsonify({'erro': 'ID, nome e email são obrigatórios'}), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar se aluno existe
        cursor.execute("SELECT id FROM alunos WHERE id = %s", (id_aluno,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        # Atualizar aluno
        cursor.execute("UPDATE alunos SET nome = %s, email = %s WHERE id = %s", 
                      (nome, email, id_aluno))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'mensagem': 'Aluno atualizado com sucesso',
            'aluno': {
                'id': id_aluno,
                'nome': nome,
                'email': email
            }
        })
        
    except MySQLdb.IntegrityError as e:
        mysql.connection.rollback()
        if 'Duplicate entry' in str(e):
            return jsonify({'erro': 'Este email já está cadastrado'}), 400
        return jsonify({'erro': 'Erro de integridade no banco de dados'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro ao atualizar aluno: {str(e)}'}), 500

@alunos_bp.route('/removealuno/<int:id>', methods=['DELETE'])
def remover_aluno(id):
    """Excluir aluno e suas matrículas"""
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar se aluno existe
        cursor.execute("SELECT nome FROM alunos WHERE id = %s", (id,))
        aluno = cursor.fetchone()
        if not aluno:
            cursor.close()
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        nome_aluno = aluno[0]
        
        # Remover matrículas do aluno
        cursor.execute("DELETE FROM matriculas WHERE aluno_id = %s", (id,))
        matriculas_removidas = cursor.rowcount
        
        # Remover aluno
        cursor.execute("DELETE FROM alunos WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'mensagem': f'Aluno "{nome_aluno}" removido com sucesso',
            'matriculas_removidas': matriculas_removidas
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro ao remover aluno: {str(e)}'}), 500
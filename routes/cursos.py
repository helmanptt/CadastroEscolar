from flask import Blueprint, request, jsonify
from database import mysql

cursos_bp = Blueprint('cursos', __name__, url_prefix='/cursos')

@cursos_bp.route('/novocurso', methods=['POST'])
def novo_curso():
    """Cadastrar novo curso"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        titulo = data.get('titulo')
        descricao = data.get('descricao')
        
        if not titulo or not descricao:
            return jsonify({'erro': 'Título e descrição são obrigatórios'}), 400
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO cursos (titulo, descricao) VALUES (%s, %s)", 
                      (titulo, descricao))
        mysql.connection.commit()
        
        curso_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'mensagem': 'Curso cadastrado com sucesso',
            'curso': {
                'id': curso_id,
                'titulo': titulo,
                'descricao': descricao
            }
        }), 201
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro ao cadastrar curso: {str(e)}'}), 500

@cursos_bp.route('', methods=['GET'])
def listar_cursos():
    """Listar todos os cursos"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, titulo, descricao FROM cursos ORDER BY titulo")
        cursos = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'cursos': [
                {
                    'id': curso[0], 
                    'titulo': curso[1], 
                    'descricao': curso[2]
                } for curso in cursos
            ],
            'total': len(cursos)
        })
    except Exception as e:
        return jsonify({'erro': f'Erro ao listar cursos: {str(e)}'}), 500

@cursos_bp.route('/<int:id>', methods=['GET'])
def detalhes_curso(id):
    """Ver detalhes de um curso"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, titulo, descricao FROM cursos WHERE id = %s", (id,))
        curso = cursor.fetchone()
        cursor.close()
        
        if curso:
            return jsonify({
                'curso': {
                    'id': curso[0], 
                    'titulo': curso[1], 
                    'descricao': curso[2]
                }
            })
        return jsonify({'erro': 'Curso não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar curso: {str(e)}'}), 500

@cursos_bp.route('/atualizacurso', methods=['PUT'])
def atualizar_curso():
    """Atualizar dados de um curso"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        id_curso = data.get('id')
        titulo = data.get('titulo')
        descricao = data.get('descricao')
        
        if not id_curso or not titulo or not descricao:
            return jsonify({'erro': 'ID, título e descrição são obrigatórios'}), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar se curso existe
        cursor.execute("SELECT id FROM cursos WHERE id = %s", (id_curso,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'erro': 'Curso não encontrado'}), 404
        
        # Atualizar curso
        cursor.execute("UPDATE cursos SET titulo = %s, descricao = %s WHERE id = %s", 
                      (titulo, descricao, id_curso))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'mensagem': 'Curso atualizado com sucesso',
            'curso': {
                'id': id_curso,
                'titulo': titulo,
                'descricao': descricao
            }
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro ao atualizar curso: {str(e)}'}), 500

@cursos_bp.route('/removecurso/<int:id>', methods=['DELETE'])
def remover_curso(id):
    """Excluir curso e suas matrículas"""
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar se curso existe
        cursor.execute("SELECT titulo FROM cursos WHERE id = %s", (id,))
        curso = cursor.fetchone()
        if not curso:
            cursor.close()
            return jsonify({'erro': 'Curso não encontrado'}), 404
        
        titulo_curso = curso[0]
        
        # Remover matrículas do curso
        cursor.execute("DELETE FROM matriculas WHERE curso_id = %s", (id,))
        matriculas_removidas = cursor.rowcount
        
        # Remover curso
        cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'mensagem': f'Curso "{titulo_curso}" removido com sucesso',
            'matriculas_removidas': matriculas_removidas
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro ao remover curso: {str(e)}'}), 500
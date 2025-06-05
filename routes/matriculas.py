from flask import Blueprint, request, jsonify
from database import mysql
import MySQLdb

matriculas_bp = Blueprint('matriculas', __name__, url_prefix='/matriculas')

@matriculas_bp.route('', methods=['POST'])
def matricular_aluno():
    """Matricular um aluno em um curso"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        aluno_id = data.get('aluno_id')
        curso_id = data.get('curso_id')
        
        if not aluno_id or not curso_id:
            return jsonify({'erro': 'aluno_id e curso_id são obrigatórios'}), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar se aluno existe
        cursor.execute("SELECT nome FROM alunos WHERE id = %s", (aluno_id,))
        aluno = cursor.fetchone()
        if not aluno:
            cursor.close()
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        # Verificar se curso existe
        cursor.execute("SELECT titulo FROM cursos WHERE id = %s", (curso_id,))
        curso = cursor.fetchone()
        if not curso:
            cursor.close()
            return jsonify({'erro': 'Curso não encontrado'}), 404
        
        # Verificar se já existe matrícula
        cursor.execute("SELECT id FROM matriculas WHERE aluno_id = %s AND curso_id = %s", 
                      (aluno_id, curso_id))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'erro': 'Aluno já está matriculado neste curso'}), 400
        
        # Criar matrícula
        cursor.execute("INSERT INTO matriculas (aluno_id, curso_id) VALUES (%s, %s)", 
                      (aluno_id, curso_id))
        mysql.connection.commit()
        
        matricula_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'mensagem': f'Aluno "{aluno[0]}" matriculado no curso "{curso[0]}" com sucesso',
            'matricula': {
                'id': matricula_id,
                'aluno_id': aluno_id,
                'aluno_nome': aluno[0],
                'curso_id': curso_id,
                'curso_titulo': curso[0]
            }
        }), 201
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'erro': f'Erro ao matricular aluno: {str(e)}'}), 500

@matriculas_bp.route('/aluno/<int:aluno_id>/cursos', methods=['GET'])
def cursos_do_aluno(aluno_id):
    """Consultar cursos que um aluno está matriculado"""
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar se aluno existe
        cursor.execute("SELECT nome FROM alunos WHERE id = %s", (aluno_id,))
        aluno = cursor.fetchone()
        if not aluno:
            cursor.close()
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        # Buscar cursos do aluno
        query = """
        SELECT c.id, c.titulo, c.descricao, m.id as matricula_id
        FROM cursos c
        INNER JOIN matriculas m ON c.id = m.curso_id
        WHERE m.aluno_id = %s
        ORDER BY c.titulo
        """
        cursor.execute(query, (aluno_id,))
        cursos = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'aluno': {
                'id': aluno_id,
                'nome': aluno[0]
            },
            'cursos': [
                {
                    'id': curso[0],
                    'titulo': curso[1],
                    'descricao': curso[2],
                    'matricula_id': curso[3]
                } for curso in cursos
            ],
            'total_cursos': len(cursos)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar cursos do aluno: {str(e)}'}), 500

@matriculas_bp.route('/curso/<int:curso_id>/alunos', methods=['GET'])
def alunos_do_curso(curso_id):
    """Consultar alunos matriculados em um curso"""
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar se curso existe
        cursor.execute("SELECT titulo FROM cursos WHERE id = %s", (curso_id,))
        curso = cursor.fetchone()
        if not curso:
            cursor.close()
            return jsonify({'erro': 'Curso não encontrado'}), 404
        
        # Buscar alunos do curso
        query = """
        SELECT a.id, a.nome, a.email, m.id as matricula_id
        FROM alunos a
        INNER JOIN matriculas m ON a.id = m.aluno_id
        WHERE m.curso_id = %s
        ORDER BY a.nome
        """
        cursor.execute(query, (curso_id,))
        alunos = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'curso': {
                'id': curso_id,
                'titulo': curso[0]
            },
            'alunos': [
                {
                    'id': aluno[0],
                    'nome': aluno[1],
                    'email': aluno[2],
                    'matricula_id': aluno[3]
                } for aluno in alunos
            ],
            'total_alunos': len(alunos)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar alunos do curso: {str(e)}'}), 500

@matriculas_bp.route('/listar', methods=['GET'])
def listar_matriculas():
    """Listar todas as matrículas (endpoint adicional para visualização)"""
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT m.id, a.id, a.nome, c.id, c.titulo
        FROM matriculas m
        INNER JOIN alunos a ON m.aluno_id = a.id
        INNER JOIN cursos c ON m.curso_id = c.id
        ORDER BY a.nome, c.titulo
        """
        cursor.execute(query)
        matriculas = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'matriculas': [
                {
                    'matricula_id': mat[0],
                    'aluno': {
                        'id': mat[1],
                        'nome': mat[2]
                    },
                    'curso': {
                        'id': mat[3],
                        'titulo': mat[4]
                    }
                } for mat in matriculas
            ],
            'total': len(matriculas)
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao listar matrículas: {str(e)}'}), 500
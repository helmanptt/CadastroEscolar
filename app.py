from flask import Flask
from database import init_db
from routes.alunos import alunos_bp
from routes.cursos import cursos_bp
from routes.matriculas import matriculas_bp

app = Flask(__name__)
init_db(app)

# Registrar blueprints
app.register_blueprint(alunos_bp)
app.register_blueprint(cursos_bp)
app.register_blueprint(matriculas_bp)

@app.route('/')
def home():
    return {
        'mensagem': 'API de Matrículas - Sistema de Gestão de Alunos e Cursos',
        'endpoints': {
            'alunos': [
                'POST /alunos/novoaluno - Cadastrar novo aluno',
                'GET /alunos - Listar todos os alunos',
                'GET /alunos/<id> - Ver detalhes de um aluno',
                'PUT /alunos/atualizaaluno - Atualizar aluno',
                'DELETE /alunos/removealuno/<id> - Excluir aluno'
            ],
            'cursos': [
                'POST /cursos/novocurso - Cadastrar novo curso',
                'GET /cursos - Listar todos os cursos',
                'GET /cursos/<id> - Ver detalhes de um curso',
                'PUT /cursos/atualizacurso - Atualizar curso',
                'DELETE /cursos/removecurso/<id> - Excluir curso'
            ],
            'matriculas': [
                'POST /matriculas - Matricular aluno em curso',
                'GET /matriculas/aluno/<id>/cursos - Cursos do aluno',
                'GET /matriculas/curso/<id>/alunos - Alunos do curso'
            ]
        }
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
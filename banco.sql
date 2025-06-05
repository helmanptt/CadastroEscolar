-- ============================================
-- SISTEMA DE MATRÍCULAS - BANCO DE DADOS
-- ============================================

CREATE DATABASE IF NOT EXISTS matriculas_db;
USE matriculas_db;

DROP TABLE IF EXISTS matriculas;
DROP TABLE IF EXISTS alunos;
DROP TABLE IF EXISTS cursos;

-- ============================================
-- TABELA ALUNOS
-- ============================================
CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABELA CURSOS
-- ============================================
CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABELA MATRICULAS (RELACIONAMENTO N:M)
-- ============================================
CREATE TABLE matriculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    curso_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_matricula (aluno_id, curso_id)
);

-- ============================================
-- DADOS DE EXEMPLO (OPCIONAL)
-- ============================================
-- Inserir alunos de exemplo
INSERT INTO alunos (nome, email) VALUES 
('João Silva', 'joao.silva@email.com'),
('Maria Santos', 'maria.santos@email.com'),
('Pedro Oliveira', 'pedro.oliveira@email.com'),
('Ana Costa', 'ana.costa@email.com');

-- Inserir cursos de exemplo
INSERT INTO cursos (titulo, descricao) VALUES 
('Análise e Desenvolvimento de Sistemas', 'Curso superior focado em desenvolvimento de software e análise de sistemas'),
('Python para Iniciantes', 'Curso básico de programação em Python'),
('Desenvolvimento Web', 'Curso completo de desenvolvimento web com HTML, CSS e JavaScript'),
('Banco de Dados MySQL', 'Curso de administração e desenvolvimento com MySQL');

-- Inserir matrículas de exemplo
INSERT INTO matriculas (aluno_id, curso_id) VALUES 
(1, 1), -- João no ADS
(1, 2), -- João no Python
(2, 1), -- Maria no ADS
(2, 3), -- Maria no Web
(3, 2), -- Pedro no Python
(3, 4), -- Pedro no MySQL
(4, 1), -- Ana no ADS
(4, 3); -- Ana no Web

-- ============================================
-- VERIFICAR ESTRUTURA CRIADA
-- ============================================
SHOW TABLES;

SELECT 'ALUNOS' as tabela, COUNT(*) as registros FROM alunos
UNION ALL
SELECT 'CURSOS' as tabela, COUNT(*) as registros FROM cursos  
UNION ALL
SELECT 'MATRICULAS' as tabela, COUNT(*) as registros FROM matriculas;

-- ============================================
-- CONSULTAS DE EXEMPLO
-- ============================================
-- Ver todas as matrículas com nomes
SELECT 
    m.id as matricula_id,
    a.nome as aluno,
    c.titulo as curso
FROM matriculas m
INNER JOIN alunos a ON m.aluno_id = a.id
INNER JOIN cursos c ON m.curso_id = c.id
ORDER BY a.nome, c.titulo;

-- Ver cursos de um aluno específico
SELECT 
    c.titulo as curso,
    c.descricao
FROM cursos c
INNER JOIN matriculas m ON c.id = m.curso_id
INNER JOIN alunos a ON m.aluno_id = a.id
WHERE a.nome = 'João Silva';

-- Ver alunos de um curso específico
SELECT 
    a.nome as aluno,
    a.email
FROM alunos a
INNER JOIN matriculas m ON a.id = m.aluno_id
INNER JOIN cursos c ON m.curso_id = c.id
WHERE c.titulo = 'Análise e Desenvolvimento de Sistemas';
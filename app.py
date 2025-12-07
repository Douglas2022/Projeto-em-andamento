from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector as my
from datetime import datetime
from mysql.connector import IntegrityError


app = Flask(__name__)
app.secret_key = "superselect123"  # NECESSÁRIO para session e flash!



# host = "douglas89.mysql.pythonanywhere-services.com"
# user = "douglas89"
# password = "Paulo#182"
# database = "douglas89$SuperSelectD"

host = "localhost" 
user = "root" 
password = "12345" 
database = "SuperSelectD"


# Função de conexão
def conectar_banco():
    return my.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

# Rota principal
@app.route('/')
def base():
    return render_template('Base.html')

# Login
# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        # Evita erro caso usuario seja None ou tipo seja NULL
        if usuario and usuario.get('senha') == senha:
            session['usuario'] = usuario.get('email')
            session['nome'] = usuario.get('nome')
            session['tipo'] = usuario.get('tipo')

            # Garantir que o campo "tipo" esteja correto antes de comparar
            tipo_usuario = (usuario.get('tipo') or '').strip().lower()

            if tipo_usuario == 'administrador':
                return redirect(url_for('administrador'))
            else:
                return redirect(url_for('produtos'))
        else:
            flash('E-mail ou senha incorretos.', 'error')
            return redirect(url_for('login'))

    return render_template('Login.html')


# Logout
@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

# Rotas públicas
@app.route('/produtos')
def produtos():
    db = conectar_banco()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('Produtos.html', produtos=produtos)

from flask import Flask, request, render_template, flash, redirect, url_for
from mysql.connector.errors import IntegrityError

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cpf = request.form['cpf']
        tipo = request.form.get('tipo', 'cliente')  # <-- CORRETO

        db = conectar_banco()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, cpf, tipo)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, email, senha, cpf, tipo))
            db.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro'))
        except IntegrityError as e:
            db.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
        finally:
            cursor.close()
            db.close()

    # GET ou se deu erro no POST
    return render_template('cadastro.html')


@app.route('/comentarios', methods=['GET', 'POST'])
def comentarios():
    db = conectar_banco()
    cursor = db.cursor(dictionary=True)

    # Buscar produtos para o select
    cursor.execute("SELECT id, nome FROM produtos")
    produtos = cursor.fetchall()

    # Filtrar produtos indesejados
    produtos = [p for p in produtos if p['nome'] not in ['Petista', 'Bolsonaro']]

    comentarios = []
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        nome_usuario = request.form.get('nome_usuario')
        texto = request.form.get('texto')

        if not produto_id or not nome_usuario or not texto:
            flash("Todos os campos são obrigatórios.", "danger")
        else:
            cursor.execute(
                "INSERT INTO comentarios (nome_usuario, texto, data_hora, produto_id) VALUES (%s, %s, NOW(), %s)",
                (nome_usuario, texto, produto_id)
            )
            db.commit()
            flash("Comentário cadastrado com sucesso!", "success")

    # Buscar comentários
    cursor.execute("""
        SELECT c.id, c.texto, c.data_hora, c.nome_usuario, p.nome AS nome_produto
        FROM comentarios c
        JOIN produtos p ON c.produto_id = p.id
        ORDER BY c.data_hora DESC
    """)
    comentarios = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('Comentario.html', comentarios=comentarios, produtos=produtos)







@app.route('/cliente')
def cliente():
    return render_template('Cliente.html')

# Rota administrador
@app.route('/administrador')
def administrador():
    db = conectar_banco()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    db.close()
    return render_template('Administrador.html', produtos=produtos)

# Salvar produto
@app.route("/salvar", methods=["POST"])
def salvar():
    db = conectar_banco()
    cursor = db.cursor()

    id = request.form.get("id")
    nome = request.form["nome"]
    marca = request.form["marca"]
    tipo = request.form["tipo"]
    preco = request.form["preco"]
    quantidade = request.form["quantidade"]
    link = request.form["link"]

    if not id:
        cursor.execute("""
            INSERT INTO produtos (nome, marca, tipo, preco, quantidade, link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, marca, tipo, preco, quantidade, link))
    else:
        cursor.execute("""
            UPDATE produtos 
            SET nome=%s, marca=%s, tipo=%s, preco=%s, quantidade=%s, link=%s
            WHERE id=%s
        """, (nome, marca, tipo, preco, quantidade, link, id))

    db.commit()
    db.close()
    return redirect("/administrador")

# Excluir produto
@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    db = conectar_banco()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE id=%s", (id,))
        db.commit()
        flash("Produto excluído com sucesso", "success")
    except Exception as e:
        db.rollback()
        flash(f"Erro ao excluir produto: {str(e)}", "danger")
    finally:
        cursor.close()
        db.close()
    return redirect("/administrador")

    

if __name__ == "__main__":
    app.run(debug=True)

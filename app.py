from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector as my


app = Flask(__name__)
app.secret_key = "superselect123"  # NECESSÁRIO para session e flash!

host = "douglas89.mysql.pythonanywhere-services.com"
user = "douglas89"
password = "Paulo#182"
database = "douglas89$SuperSelectD"

#Paulo#182
#douglas89
#douglas89.mysql.pythonanywhere-services.com

# host = "localhost" 
# user = "root" 
# password = "12345" 
# database = "SuperSelectD"


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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        # Aqui a senha é verificada como texto simples
        if usuario and usuario['senha'] == senha:
            session['usuario'] = usuario['email']
            session['nome'] = usuario['nome']
            session['tipo'] = usuario['tipo']

            if usuario['tipo'].strip().lower() == 'administrador':
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

@app.route('/cadastro')
def cadastro():
    return render_template('Cadastro.html')

@app.route('/comentarios')
def comentarios():
    return render_template('Comentarios.html')

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
@app.route("/excluir/<int:id>")
def excluir(id):
    db = conectar_banco()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect("/administrador")

if __name__ == "__main__":
    app.run(debug=True)

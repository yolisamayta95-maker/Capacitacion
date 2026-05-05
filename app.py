from flask import Flask, request, redirect, render_template,url_for,flash
import sqlite3
app = Flask(__name__)
app.secret_key = 'Unaclavesecreta'

#funcion para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect("instituto.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return redirect(url_for('estudiantes'))

@app.route("/estudiantes")
def estudiantes():
    conn = get_db_connection()
    estudiantes = conn.execute('SELECT * FROM estudiantes').fetchall()
    conn.close()
    return render_template('estudiantes.html',estudiantes=estudiantes)

@app.route("/cursos")
def cursos():
    conn = get_db_connection()
    cursos = conn.execute('SELECT * FROM cursos').fetchall()
    conn.close()
    return render_template('cursos.html',cursos=cursos)

@app.route("/curso/nuevo", methods=['GET','POST'])
def nuevo_curso():
    if request.method == 'POST':
        #leer contenido del formulario
        descripcion = request.form['descripcion']
        horas = request.form['horas']
        
        conn = get_db_connection()
        conn.execute("INSERT INTO cursos (descripcion,horas) VALUES (?,?)",
                     (descripcion,horas))
        
        conn.commit()
        conn.close()
        flash('curso agregado correctamente','success')
        return redirect(url_for('cursos'))
        
    return render_template('form_curso.html')

@app.route('/curso/editar/<int:id>', methods=['GET','POST'])
def editar_curso(id):
    conn = get_db_connection()
    curso = conn.execute("SELECT * FROM cursos WHERE id = ?",(id,)).fetchone()
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        horas = request.form['horas']
        
        conn.execute("UPDATE cursos SET descripcion = ?, horas = ? WHERE id = ?",
        (descripcion,horas,id))
        conn.commit()
        conn.close()
        flash('curso actualizado','succes')
        return redirect(url_for('cursos'))
    
    return render_template('form_curso.html',curso=curso)

@app.route('/curso/eliminar/<int:id>')
def eliminar_curso(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM cursos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash('curso eliminado','success')
    return redirect(url_for('cursos'))

@app.route("/inscripciones")
def inscripciones():
    conn = get_db_connection()
    inscripciones = conn.execute(
        """
        SELECT i.id, i.fecha,
            e.nombre || ' ' || e.apellidos as estudiante,
            c.descripcion as curso
        FROM inscripciones i
        JOIN estudiantes e ON i.estudiante_id = e.id
        JOIN cursos c ON i.curso_id = c.id
        """
    ).fetchall()
    conn.close()
    return render_template('inscripciones.html',inscripciones=inscripciones)

@app.route("/inscripcion/nuevo",methods=['GET','POST'])
def nueva_inscripcion():
    conn = get_db_connection()
    #en caso de que sea post, consolidar la inscripcion
    if request.method == 'POST':
        fecha = request.form['fecha']
        estudiante_id = request.form['estudiante_id']
        curso_id = request.form['curso_id']
        
        conn.execute(
            """
            INSERT INTO inscripciones
            (fecha, estudiante_id, curso_id)
            VALUES (?,?,?)
            """,
            (fecha, estudiante_id, curso_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("inscripciones"))
    # en caso de get enviar datos para mostrar el formulario de inscripcion
    estudiantes = conn.execute(
        """
        SELECT id, nombre || ' ' || apellidos as nombre
        FROM estudiantes
        """
    ).fetchall()
    cursos = conn.execute(
        """
        SELECT id, descripcion FROM cursos
        """
    ).fetchall()
    conn.close()
    return render_template('form_inscripcion.html',estudiantes=estudiantes,cursos=cursos)
    
    
@app.route('/inscripcion/eliminar/<int:id>')
def eliminar_inscripcion(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM inscripciones WHERE id = ?",(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('inscripciones'))

if __name__ == "__main__":
    app.run(debug=True)
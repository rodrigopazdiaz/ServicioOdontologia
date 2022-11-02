import os
from flask import Flask, render_template, request, redirect, send_from_directory, session
from flaskext.mysql import MySQL
app=Flask(__name__)
app.secret_key="rodrigopaz"
mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='odontologia'
mysql.init_app(app)
@app.route('/')
def inicio():
    if not 'login' in session:
        return redirect("/login")
    return render_template('sitio/index.html')

@app.route('/login')
def login():
    return render_template('sitio/login.html')


@app.route('/login', methods=['POST'])
def login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    if _usuario=="carlospaz" and _password=="123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/")
    return render_template('sitio/login.html',mensaje="Acceso denegado")

@app.route('/consulta')
def consulta():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT ID_Atencion, paciente.Nombre, atencion.Tratamiento, Fecha_Atencion FROM `paciente` JOIN `atencion` ON paciente.ID_Paciente=atencion.ID_Paciente")
    datosconsulta=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/consulta.html',datosconsulta=datosconsulta)

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route('/imgpaciente/<imagen>')
def imgpaciente(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/imgpaciente'),imagen)   

@app.route("/js/<archivojs>")
def js_link(archivojs):
    return send_from_directory(os.path.join('templates/sitio/js'),archivojs) 

@app.route('/imagenes', methods=['POST'])
def imagenespaciente():
    _idp=request.form['txtIDp']
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT Nombre FROM `paciente` WHERE ID_Paciente=%s",(_idp))
    datospaciente=cursor.fetchall()
    conexion.commit()
    print(datospaciente[0][0])
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `imagen` WHERE ID_Paciente=%s",(_idp))
    datosimagen=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/imagenes.html',datospaciente=datospaciente,datosimagen=datosimagen)

@app.route('/imagenes/guardar', methods=['POST'])
def imagenespacienteguardar():
    _nombrep=request.form['txtNamePaciente']
    _imgm=request.files['txtImgMaterial']
    _titleimg=request.form['txtTituloImagen']
    _intm=request.form['txtDescrImagen']
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT ID_Paciente FROM `paciente` WHERE Nombre=%s",(_nombrep))
    datospaciente=cursor.fetchall()
    conexion.commit()
    if _imgm.filename!="":
        _imgm.save("templates/sitio/imgpaciente/"+_imgm.filename)
    sql="INSERT INTO `imagen` ( `ID_Imagen`, `ID_Paciente`, `Nombre_IMG`, `Titulo`, `Descripcion`) VALUES (NULL,%s,%s,%s,%s);"
    datos=(datospaciente[0][0],_imgm.filename,_titleimg,_intm)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    return redirect('/pacientes')

@app.route('/pacientes')
def pacientes():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT ID_Paciente, Nombre, Apellido, Telefono, Diagnosis, Deuda FROM `paciente`")
    datospaciente=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/pacientes.html',datospaciente=datospaciente)  

@app.route('/cronograma')
def cronograma():
    return render_template('sitio/cronograma.html')   

@app.route('/infoclinica')
def info_clinica():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `clinica`")
    datosdoctor=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/info_clinica.html',datosdoctor=datosdoctor)   

@app.route('/detallesatencion', methods=['POST'])
def detalles_atencion():
    _idc=request.form['txtIDc']
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT paciente.Nombre, paciente.Apellido, paciente.Diagnosis, atencion.Tratamiento, atencion.Fecha_Atencion, atencion.Costo_Total from `atencion` INNER JOIN `paciente`  ON paciente.ID_Paciente=atencion.ID_Paciente WHERE ID_Atencion=%s",(_idc))
    d1=cursor.fetchall()
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT clinica.Nombre from `atencion` INNER JOIN `clinica`  ON clinica.ID_Doctor=atencion.ID_Doctor WHERE ID_Atencion=%s",(_idc))
    d2=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/detalles_atencion.html',d1=d1,d2=d2)

@app.route('/detallespaciente', methods=['POST'])
def detalles_paciente():
    _idp=request.form['txtIDp']
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `paciente` WHERE ID_Paciente=%s",(_idp))
    datospacienteall=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/detallespaciente.html',datospacienteall=datospacienteall)

@app.route('/procedimientospaciente', methods=['POST'])
def procedimientos_paciente():
    _idp=request.form['txtIDp']
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `proced_paciente` WHERE Id_Paciente=%s",(_idp))
    datosprocpacienteall=cursor.fetchall()
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT Costo_Proc FROM `proced_paciente` WHERE Id_Paciente=%s",(_idp))
    datossumacosto=cursor.fetchall()
    a=0
    for i in datossumacosto:
        a=a+i[0]
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT Nombre_Operacion, Costo_Unitario_Operacion  FROM `operacion` WHERE Id_Paciente=%s",(_idp))
    datossumaop=cursor.fetchall()
    b=0
    for i in datossumaop:
        b=b+i[1]
    conexion.commit()
    c=a-b
    c=round(c,2)
    return render_template('sitio/procedimientos_paciente.html',datosprocpacienteall=datosprocpacienteall,datossumaop=datossumaop,c=c)

@app.route('/newconsulta')
def newconsulta():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT ID_Paciente, Nombre FROM `paciente`")
    nombrep=cursor.fetchall()
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT ID_Doctor, Nombre FROM `clinica`")
    nombred=cursor.fetchall()
    conexion.commit()

    return render_template('sitio/newconsulta.html',nombrep=nombrep,nombred=nombred)

@app.route('/newconsulta/guardar', methods=['POST'])
def newconsulta_guardar():
    _IDP=request.form['txtIDP']
    _IDD=request.form['txtIDD']
    _DiagnosisC=request.form['txtDiagnosisC']
    _FA=request.form['txtFA']
    _IDM=request.form['txtCostoT']
    sql="INSERT INTO `atencion` ( `ID_Atencion`, `ID_Paciente`, `ID_Doctor`, `Tratamiento`, `Fecha_Atencion`, `Costo_Total`) VALUES (NULL,%s,%s,%s,%s,%s);"
    datos=(_IDP,_IDD,_DiagnosisC,_FA,_IDM)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    sql="INSERT INTO `proced_paciente` ( `Id_Proc`, `ID_Paciente`, `Fecha_Proc`, `Nombre_Proc`, `Costo_Proc`) VALUES (NULL,%s,%s,%s,%s);"
    datos=(_IDP,_FA,_DiagnosisC,_IDM)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT Deuda FROM `paciente` WHERE Id_Paciente=%s",(_IDP))
    d1=cursor.fetchone()
    conexion.commit()
    a=float(_IDM)
    b=0
    b=d1[0]-a
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("UPDATE `paciente` SET Deuda=%s WHERE Id_Paciente=%s",(b,_IDP))
    conexion.commit()
    return redirect('/consulta')    

@app.route('/newpaciente')
def newpaciente():
    return render_template('sitio/newPaciente.html')

@app.route('/newdoctor')
def newdoctor():
    return render_template('sitio/newdoctor.html')

@app.route('/newdoctor/guardar', methods=['POST'])
def newdoctor_guardar():
    _nombred=request.form['txtNombreD']
    _telefonod=request.form['txtTelefonoD']
    _direcciond=request.form['txtDireccionD']
    _horainiciod=request.form['txtHoraInicioD']
    _horafind=request.form['txtHoraFinD']
    sql="INSERT INTO `clinica` ( `ID_Doctor`, `Nombre`, `Telefono`, `Direccion`, `Hora_Inicio`, `Hora_Fin`) VALUES (NULL,%s,%s,%s,%s,%s);"
    datos=(_nombred,_telefonod,_direcciond,_horainiciod,_horafind)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    return redirect('/infoclinica')

@app.route('/newpaciente/guardar', methods=['POST'])
def newpaciente_guardar():
    _nombrep=request.form['txtNombreP']
    _apellidop=request.form['txtApellidoP']
    _telefonop=request.form['txtTelefonoP']
    _correop=request.form['txtCorreoP']
    _direccionp=request.form['txtDireccionP']
    _dnip=request.form['txtDniP']
    _diagnosisp=request.form['txtDiagnosisP']
    sql="INSERT INTO `paciente` ( `ID_Paciente`, `Nombre`, `Apellido`, `Telefono`, `Correo`, `Direccion`, `DNI`, `Diagnosis`, `Deuda`) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,0);"
    datos=(_nombrep,_apellidop,_telefonop,_correop,_direccionp,_dnip,_diagnosisp)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    return redirect('/pacientes')

@app.route('/procedimientos')
def procedimientos():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT ID_Paciente, Nombre FROM `paciente`")
    nombrep=cursor.fetchall()
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT paciente.nombre, operacion.Nombre_Operacion, operacion.Costo_Unitario_Operacion FROM `operacion` INNER JOIN `paciente` WHERE paciente.ID_Paciente=operacion.ID_Paciente")
    datosoperacion=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/procedimiento.html',datosoperacion=datosoperacion,nombrep=nombrep)

@app.route('/procedimientos/guardar', methods=['POST'])
def procedimientos_guardar():
    _IDP=request.form['txtNamePaciente']
    _nombreop=request.form['txtNameOperation']
    _costoop=request.form['txtCostOperation']
    sql="INSERT INTO `operacion` ( `ID_Operacion`, `ID_Paciente`, `Nombre_Operacion`, `Costo_Unitario_Operacion`) VALUES (NULL,%s,%s,%s);"
    datos=(_IDP,_nombreop,_costoop)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT Deuda FROM `paciente` WHERE Id_Paciente=%s",(_IDP))
    d1=cursor.fetchone()
    conexion.commit()
    a=float(_costoop)
    b=0
    b=d1[0]+a
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("UPDATE `paciente` SET Deuda=%s WHERE Id_Paciente=%s",(b,_IDP))
    conexion.commit()
    return redirect('/procedimientos')

@app.route('/materiales')
def materiales():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `material`")
    datosmateriales=cursor.fetchall()
    conexion.commit()
    return render_template('sitio/materiales.html',datosmateriales=datosmateriales)

@app.route('/materiales/guardar', methods=['POST'])
def materiales_guardar():
    _nombrem=request.form['txtNameMaterial']
    _imgm=request.files['txtImgMaterial']
    _typem=request.form['txtTypeMaterial']
    _intm=request.form['txtIntMaterial']
    _costm=request.form['txtCostMaterial']
    if _imgm.filename!="":
        _imgm.save("templates/sitio/img/"+_imgm.filename)
    sql="INSERT INTO `material` ( `ID_Material`, `Nombre_Material`, `IMG_Material`, `Tipo_Material`, `Cant_Material`, `Costo_Material`) VALUES (NULL,%s,%s,%s,%s,%s);"
    datos=(_nombrem,_imgm.filename,_typem,_intm,_costm)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    return redirect('/materiales')              

if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import request, render_template, redirect, url_for
import pymongo
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

from app import app, productos

def consultarProductoPorCodigo(codigo):
    try:
        consulta = {"codigo": codigo}
        producto = productos.find_one(consulta)
        return producto is not None
    except pymongo.errors.PyMongoError as error:
        print(error)
        return False

@app.route("/")
def inicio():
    listaProductos = productos.find()
    return render_template("listarProductos.html", listaProductos=listaProductos)

@app.route("/frmAgregarProducto")
def vistaAgregar():
    return render_template("frmAgregarProducto.html")

@app.route("/agregarProducto", methods=["POST"])
def agregarProducto():
    try:
        codigo = int(request.form["txtCodigo"])
        nombre = request.form["txtNombre"]
        precio = int(request.form["txtPrecio"])
        categoria = request.form["cbCategoria"]
        
        archivo = request.files["fileFoto"]
        nombreArchivo = secure_filename(archivo.filename)
        listaNombreArchivo = nombreArchivo.rsplit(".", 1)
        extension = listaNombreArchivo[1].lower() if len(listaNombreArchivo) > 1 else "jpg"

        producto = {
            "codigo": codigo,
            "nombre": nombre,
            "precio": precio,
            "categoria": categoria
        }

        if consultarProductoPorCodigo(codigo):
            mensaje = "Ya existe un producto con ese código"
            return render_template("frmAgregarProducto.html", producto=producto, mensaje=mensaje)

        resultado = productos.insert_one(producto)
        if resultado.acknowledged:
            idProducto = resultado.inserted_id
            nuevoNombre = f"{idProducto}.{extension}"
            archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nuevoNombre))
            return redirect("/")
            
    except pymongo.errors.PyMongoError as error:
        return render_template("frmAgregarProducto.html", producto={}, mensaje=str(error))

@app.route("/consultar/<string:idProducto>", methods=["GET"])
def consultarPorId(idProducto):
    try:
        idObj = ObjectId(idProducto)
        consulta = {"_id": idObj}
        producto = productos.find_one(consulta)
        return render_template("frmEditarProducto.html", producto=producto)
    except pymongo.errors.PyMongoError as error:
        listaProductos = productos.find()
        return render_template("listarProductos.html", mensaje=str(error), listaProductos=listaProductos)

@app.route("/actualizar", methods=["POST"])
def actualizarProducto():
    try:
        codigo = int(request.form["txtCodigo"])
        nombre = request.form["txtNombre"]
        precio = int(request.form["txtPrecio"])
        categoria = request.form["cbCategoria"]
        idProducto = ObjectId(request.form["idProducto"])

        criterio = {"_id": idProducto}
        datosActualizar = {
            "codigo": codigo,
            "nombre": nombre,
            "precio": precio,
            "categoria": categoria
        }

        resultado = productos.update_one(criterio, {"$set": datosActualizar})

        if resultado.acknowledged:
            archivo = request.files.get("fileFoto")
            if archivo and archivo.filename != "":
                nombreArchivo = secure_filename(archivo.filename)
                extension = nombreArchivo.rsplit(".", 1)[1].lower()
                nombreArchivoActualizar = f"{idProducto}.{extension}"
                archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombreArchivoActualizar))
        return redirect("/")
    except pymongo.errors.PyMongoError as error:
        listaProductos = productos.find()
        return render_template("listarProductos.html", mensaje=str(error), listaProductos=listaProductos)

@app.route("/eliminar/<string:idProducto>", methods=["GET"])
def eliminarProducto(idProducto):
    try:
        idObj = ObjectId(idProducto)
        resultado = productos.delete_one({"_id": idObj})
        if resultado.acknowledged:
            mensaje = "Producto eliminado"
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    return redirect("/")
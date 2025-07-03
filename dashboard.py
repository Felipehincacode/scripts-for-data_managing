# -*- coding: utf-8 -*-

"""
Dashboard Principal de Flowbooster.

Este archivo define la interfaz principal con tarjetas para todas las
funcionalidades disponibles del programa.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QScrollArea, QSizePolicy, QSpacerItem, QDialog,
    QComboBox, QCheckBox, QFileDialog, QMessageBox, QProgressBar, QLineEdit, QSlider
)
from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import QFont, QDesktopServices, QCursor, QMovie, QPixmap, QPainter, QColor, QBrush
import sys
import os
from core import procesar_proyecto, procesar_proyecto_por_fecha, abrir_carpeta

APP_VERSION = "v2.0.0"

class TarjetaFuncionalidad(QFrame):
    """
    Widget de tarjeta para representar una funcionalidad del programa.
    """
    def __init__(self, titulo, descripcion, icono, color, parent=None):
        super().__init__(parent)
        self.setObjectName("tarjeta")
        self.setProperty("color", color)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumSize(280, 180)
        self.setMaximumSize(320, 200)
        
        # Layout principal de la tarjeta
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Icono y título
        icono_label = QLabel(icono)
        icono_label.setAlignment(Qt.AlignCenter)
        icono_label.setStyleSheet("font-size: 32px; margin-bottom: 8px;")
        
        titulo_label = QLabel(titulo)
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        descripcion_label = QLabel(descripcion)
        descripcion_label.setAlignment(Qt.AlignCenter)
        descripcion_label.setWordWrap(True)
        descripcion_label.setStyleSheet("font-size: 12px; color: #cccccc; line-height: 1.4;")
        
        layout.addWidget(icono_label)
        layout.addWidget(titulo_label)
        layout.addWidget(descripcion_label)
        layout.addStretch()

class OrganizadorPorTipoDialog(QDialog):
    """
    Diálogo para la funcionalidad de organización por tipo de archivo.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Organizar por Tipo de Archivo")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #212121; color: #e0e0e0;")
        
        self.origen = ""
        self.destino = ""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("📁 Organizar por Tipo de Archivo")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #bb86fc;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Descripción
        desc = QLabel("Organiza tus archivos en carpetas separadas por tipo: JPG, RAW, Videos")
        desc.setStyleSheet("font-size: 14px; color: #cccccc;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Selección de carpetas
        self.btn_origen = QPushButton("📂 Seleccionar Carpeta de Origen")
        self.btn_destino = QPushButton("📁 Seleccionar Carpeta de Destino")
        layout.addWidget(self.btn_origen)
        layout.addWidget(self.btn_destino)
        
        # Opciones
        self.checkbox_copiar = QCheckBox("Copiar archivos (en lugar de moverlos)")
        self.checkbox_crear_todas = QCheckBox("Crear todas las carpetas (incluso vacías)")
        self.checkbox_readme = QCheckBox("Incluir archivos README.md")
        layout.addWidget(self.checkbox_copiar)
        layout.addWidget(self.checkbox_crear_todas)
        layout.addWidget(self.checkbox_readme)
        
        # Botón de acción
        self.btn_organizar = QPushButton("🚀 ORGANIZAR")
        self.btn_organizar.setStyleSheet("""
            QPushButton {
                background-color: #bb86fc;
                color: #121212;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d1b3ff;
            }
        """)
        layout.addWidget(self.btn_organizar)
        
        # Barra de progreso
        self.progreso = QProgressBar()
        self.progreso.setVisible(False)
        layout.addWidget(self.progreso)
        
        # Conexiones
        self.btn_origen.clicked.connect(self.seleccionar_origen)
        self.btn_destino.clicked.connect(self.seleccionar_destino)
        self.btn_organizar.clicked.connect(self.organizar)
    
    def seleccionar_origen(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📂 Seleccionar Carpeta Origen")
        if carpeta:
            self.origen = carpeta
            self.btn_origen.setText(f"📂 Origen: {os.path.basename(carpeta)}")
    
    def seleccionar_destino(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📁 Seleccionar Carpeta Destino")
        if carpeta:
            self.destino = carpeta
            self.btn_destino.setText(f"📁 Destino: {os.path.basename(carpeta)}")
    
    def organizar(self):
        if not self.origen or not self.destino:
            QMessageBox.warning(self, "⚠️ Error", "Debes seleccionar ambas carpetas.")
            return
        
        copiar = self.checkbox_copiar.isChecked()
        crear_todas = self.checkbox_crear_todas.isChecked()
        incluir_readme = self.checkbox_readme.isChecked()
        
        log, tipo_proyecto = procesar_proyecto(self.origen, self.destino, copiar, crear_todas, incluir_readme)
        
        if tipo_proyecto == "vacio":
            QMessageBox.information(self, "ℹ️ Sin archivos", "No hay archivos para procesar en la carpeta origen.")
            return
        
        accion_str = "copiados" if copiar else "movidos"
        mensaje = f"✅ ¡Éxito! {len(log)} archivos {accion_str}.\n📂 Proyecto: {tipo_proyecto}"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Proceso finalizado")
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        if msg_box.exec() == QMessageBox.Yes:
            abrir_carpeta(self.destino)
        
        self.accept()

class OrganizadorPorFechaDialog(QDialog):
    """
    Diálogo para la funcionalidad de organización por fecha.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Organizar por Fecha")
        self.setMinimumSize(500, 450)
        self.setStyleSheet("background-color: #212121; color: #e0e0e0;")
        
        self.origen = ""
        self.destino = ""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("📅 Organizar por Fecha")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #bb86fc;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Descripción
        desc = QLabel("Organiza tus archivos en carpetas por fecha de creación (EXIF o modificación)")
        desc.setStyleSheet("font-size: 14px; color: #cccccc;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Selección de carpetas
        self.btn_origen = QPushButton("📂 Seleccionar Carpeta de Origen")
        self.btn_destino = QPushButton("📁 Seleccionar Carpeta de Destino")
        layout.addWidget(self.btn_origen)
        layout.addWidget(self.btn_destino)
        
        # Nivel de organización
        nivel_label = QLabel("Nivel de organización:")
        nivel_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(nivel_label)
        
        self.combo_nivel = QComboBox()
        self.combo_nivel.addItems([
            "Día (2024-01-15)",
            "Semana (2024-W03)", 
            "Mes (2024-01)",
            "Año (2024)"
        ])
        self.combo_nivel.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                border: 2px solid #444444;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #bb86fc;
            }
        """)
        layout.addWidget(self.combo_nivel)
        
        # Opciones
        self.checkbox_copiar = QCheckBox("Copiar archivos (en lugar de moverlos)")
        self.checkbox_readme = QCheckBox("Incluir archivos README.md")
        layout.addWidget(self.checkbox_copiar)
        layout.addWidget(self.checkbox_readme)
        
        # Botón de acción
        self.btn_organizar = QPushButton("🚀 ORGANIZAR")
        self.btn_organizar.setStyleSheet("""
            QPushButton {
                background-color: #bb86fc;
                color: #121212;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d1b3ff;
            }
        """)
        layout.addWidget(self.btn_organizar)
        
        # Conexiones
        self.btn_origen.clicked.connect(self.seleccionar_origen)
        self.btn_destino.clicked.connect(self.seleccionar_destino)
        self.btn_organizar.clicked.connect(self.organizar)
    
    def seleccionar_origen(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📂 Seleccionar Carpeta Origen")
        if carpeta:
            self.origen = carpeta
            self.btn_origen.setText(f"📂 Origen: {os.path.basename(carpeta)}")
    
    def seleccionar_destino(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📁 Seleccionar Carpeta Destino")
        if carpeta:
            self.destino = carpeta
            self.btn_destino.setText(f"📁 Destino: {os.path.basename(carpeta)}")
    
    def organizar(self):
        if not self.origen or not self.destino:
            QMessageBox.warning(self, "⚠️ Error", "Debes seleccionar ambas carpetas.")
            return
        
        # Mapear el nivel seleccionado
        nivel_map = {
            0: "dia",
            1: "semana", 
            2: "mes",
            3: "año"
        }
        nivel_organizacion = nivel_map[self.combo_nivel.currentIndex()]
        
        copiar = self.checkbox_copiar.isChecked()
        incluir_readme = self.checkbox_readme.isChecked()
        
        log, total_archivos = procesar_proyecto_por_fecha(
            self.origen, self.destino, nivel_organizacion, copiar, incluir_readme
        )
        
        if total_archivos == 0:
            QMessageBox.information(self, "ℹ️ Sin archivos", "No hay archivos para procesar en la carpeta origen.")
            return
        
        accion_str = "copiados" if copiar else "movidos"
        mensaje = f"✅ ¡Éxito! {total_archivos} archivos {accion_str}.\n📂 Organizados por {nivel_organizacion}"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Proceso finalizado")
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        if msg_box.exec() == QMessageBox.Yes:
            abrir_carpeta(self.destino)
        
        self.accept()

class CompararEmparejarDialog(QDialog):
    """
    Diálogo para comparar dos carpetas y mover archivos sin pareja a una sola carpeta.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparar y Mover No Emparejadas")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #212121; color: #e0e0e0;")
        self.carpeta_a = ""
        self.carpeta_b = ""
        self.carpeta_salida = ""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        titulo = QLabel("🔗 Comparar y Mover No Emparejadas")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #bb86fc;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        desc = QLabel("Selecciona dos carpetas. Se moverán los archivos de ambas carpetas que no tengan pareja en la otra, a una sola carpeta de salida.")
        desc.setStyleSheet("font-size: 14px; color: #cccccc;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        self.btn_a = QPushButton("📂 Seleccionar Carpeta 1")
        self.btn_b = QPushButton("📂 Seleccionar Carpeta 2")
        self.btn_salida = QPushButton("📁 Seleccionar Carpeta de Salida")
        layout.addWidget(self.btn_a)
        layout.addWidget(self.btn_b)
        layout.addWidget(self.btn_salida)
        self.btn_comparar = QPushButton("🚀 COMPARAR Y MOVER")
        self.btn_comparar.setStyleSheet("""
            QPushButton {
                background-color: #bb86fc;
                color: #121212;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d1b3ff;
            }
        """)
        layout.addWidget(self.btn_comparar)
        self.btn_a.clicked.connect(self.seleccionar_a)
        self.btn_b.clicked.connect(self.seleccionar_b)
        self.btn_salida.clicked.connect(self.seleccionar_salida)
        self.btn_comparar.clicked.connect(self.comparar_y_mover)
    def seleccionar_a(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📂 Seleccionar Carpeta 1")
        if carpeta:
            self.carpeta_a = carpeta
            self.btn_a.setText(f"📂 Carpeta 1: {os.path.basename(carpeta)}")
    def seleccionar_b(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📂 Seleccionar Carpeta 2")
        if carpeta:
            self.carpeta_b = carpeta
            self.btn_b.setText(f"📂 Carpeta 2: {os.path.basename(carpeta)}")
    def seleccionar_salida(self):
        carpeta = QFileDialog.getExistingDirectory(self, "📁 Seleccionar Carpeta de Salida")
        if carpeta:
            self.carpeta_salida = carpeta
            self.btn_salida.setText(f"📁 Salida: {os.path.basename(carpeta)}")
    def comparar_y_mover(self):
        if not self.carpeta_a or not self.carpeta_b or not self.carpeta_salida:
            QMessageBox.warning(self, "⚠️ Error", "Debes seleccionar las tres carpetas.")
            return
        from core import mover_no_emparejadas_ambas
        movidos = mover_no_emparejadas_ambas([self.carpeta_a, self.carpeta_b], self.carpeta_salida)
        mensaje = f"✅ Proceso finalizado.\n\nArchivos sin pareja movidos: {len(movidos)}\n\n¿Abrir carpeta de salida?"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Comparación finalizada")
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        if msg_box.exec() == QMessageBox.Yes:
            abrir_carpeta(self.carpeta_salida)
        self.accept()

class ComprimirParticionarDialog(QDialog):
    """
    Diálogo intuitivo para comprimir y particionar carpetas seleccionadas, con barra de progreso y subida opcional a SwissTransfer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comprimir y Particionar Carpetas")
        self.setMinimumSize(600, 600)
        self.setStyleSheet("background-color: #212121; color: #e0e0e0;")
        self.carpetas = []
        self.destino = ""
        self.archivos_generados = []
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)
        # Título
        titulo = QLabel("🗜️ Comprimir y Particionar Carpetas")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #bb86fc;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        # Explicación general
        explic = QLabel("Selecciona varias carpetas para comprimirlas en un solo archivo ZIP. Puedes protegerlo con contraseña y dividirlo en partes. Al finalizar, puedes subirlo fácilmente a SwissTransfer.")
        explic.setWordWrap(True)
        explic.setStyleSheet("font-size: 13px; color: #cccccc;")
        layout.addWidget(explic)
        # Selector visual de carpetas
        self.lista_carpetas = QVBoxLayout()
        self.lista_carpetas.setSpacing(6)
        self.lista_carpetas.setAlignment(Qt.AlignTop)
        self.widget_lista = QWidget()
        self.widget_lista.setLayout(self.lista_carpetas)
        layout.addWidget(QLabel("Carpetas a comprimir:"))
        layout.addWidget(self.widget_lista)
        btns_h = QHBoxLayout()
        self.btn_add = QPushButton("+ Añadir carpeta")
        self.btn_add.setToolTip("Agregar una carpeta de entrada")
        btns_h.addWidget(self.btn_add)
        btns_h.addStretch()
        layout.addLayout(btns_h)
        # Carpeta de destino
        self.btn_destino = QPushButton("📁 Seleccionar Carpeta de Destino")
        self.btn_destino.setToolTip("El archivo ZIP se guardará aquí")
        layout.addWidget(self.btn_destino)
        # Nombre automático
        layout.addWidget(QLabel("Nombre automático del ZIP:"))
        self.combo_nombre = QComboBox()
        self.combo_nombre.addItems(["Por nombre fijo (comprimido.zip)", "Por fecha actual", "Por fecha de última edición"])
        self.combo_nombre.setToolTip("Elige cómo se nombrará el archivo comprimido")
        layout.addWidget(self.combo_nombre)
        # Contraseña
        self.checkbox_pass = QCheckBox("Proteger con contraseña (opcional)")
        self.checkbox_pass.setToolTip("El ZIP estará protegido. ¡No olvides la contraseña!")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setPlaceholderText("Contraseña opcional")
        self.input_pass.setEnabled(False)
        layout.addWidget(self.checkbox_pass)
        layout.addWidget(self.input_pass)
        # Particionado opcional
        self.checkbox_partes = QCheckBox("Particionar en partes (opcional)")
        self.checkbox_partes.setToolTip("Divide el ZIP en partes más pequeñas para facilitar la subida o el envío.")
        layout.addWidget(self.checkbox_partes)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(10240)
        self.slider.setValue(4096)
        self.slider.setTickInterval(100)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.label_slider = QLabel("4096 MB (4 GB)")
        self.slider.setVisible(False)
        self.label_slider.setVisible(False)
        layout.addWidget(self.slider)
        layout.addWidget(self.label_slider)
        # SwissTransfer opcional
        self.checkbox_swiss = QCheckBox("Abrir SwissTransfer al finalizar")
        self.checkbox_swiss.setChecked(False)
        self.checkbox_swiss.setToolTip("Abre el navegador en SwissTransfer para subir el archivo comprimido.")
        layout.addWidget(self.checkbox_swiss)
        # Resumen
        self.label_resumen = QLabel()
        self.label_resumen.setStyleSheet("font-size: 13px; color: #bb86fc; margin-top: 10px;")
        layout.addWidget(self.label_resumen)
        # Botón de acción
        self.btn_comprimir = QPushButton("🚀 COMPRIMIR")
        self.btn_comprimir.setStyleSheet("""
            QPushButton {
                background-color: #bb86fc;
                color: #121212;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d1b3ff;
            }
        """)
        layout.addWidget(self.btn_comprimir)
        # Barra de progreso emergente
        self.progress_dialog = None
        # Conexiones
        self.btn_add.clicked.connect(self.agregar_carpeta)
        self.btn_destino.clicked.connect(self.seleccionar_destino)
        self.checkbox_pass.stateChanged.connect(self.toggle_pass)
        self.checkbox_partes.stateChanged.connect(self.toggle_partes)
        self.slider.valueChanged.connect(self.actualizar_slider)
        self.btn_comprimir.clicked.connect(self.comprimir)
        self.actualizar_lista()
        self.actualizar_resumen()
    def agregar_carpeta(self):
        from PySide6.QtWidgets import QFileDialog
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta a comprimir")
        if carpeta and carpeta not in self.carpetas:
            self.carpetas.append(carpeta)
            self.actualizar_lista()
            self.actualizar_resumen()
    def eliminar_carpeta(self, carpeta):
        self.carpetas = [c for c in self.carpetas if c != carpeta]
        self.actualizar_lista()
        self.actualizar_resumen()
    def actualizar_lista(self):
        # Limpiar lista
        for i in reversed(range(self.lista_carpetas.count())):
            item = self.lista_carpetas.itemAt(i).widget()
            if item:
                item.setParent(None)
        # Agregar cada carpeta con botón de eliminar
        for carpeta in self.carpetas:
            h = QHBoxLayout()
            label = QLabel(os.path.basename(carpeta))
            label.setToolTip(carpeta)
            btn_del = QPushButton("✕")
            btn_del.setFixedWidth(28)
            btn_del.setStyleSheet("color:#fff;background:#bb86fc;border:none;border-radius:14px;font-weight:bold;")
            btn_del.clicked.connect(lambda _, c=carpeta: self.eliminar_carpeta(c))
            h.addWidget(label)
            h.addWidget(btn_del)
            h.addStretch()
            w = QWidget()
            w.setLayout(h)
            self.lista_carpetas.addWidget(w)
    def seleccionar_destino(self):
        from PySide6.QtWidgets import QFileDialog
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        if carpeta:
            self.destino = carpeta
            self.btn_destino.setText(f"📁 Destino: {os.path.basename(carpeta)}")
            self.actualizar_resumen()
    def toggle_pass(self, state):
        self.input_pass.setEnabled(state == Qt.Checked)
        self.actualizar_resumen()
    def toggle_partes(self, state):
        visible = state == Qt.Checked
        self.slider.setVisible(visible)
        self.label_slider.setVisible(visible)
        self.actualizar_resumen()
    def actualizar_slider(self, value):
        gb = value / 1024
        if gb >= 1:
            self.label_slider.setText(f"{value} MB ({gb:.2f} GB)")
        else:
            self.label_slider.setText(f"{value} MB")
        self.actualizar_resumen()
    def actualizar_resumen(self):
        resumen = f"<b>Resumen:</b><br>"
        if not self.carpetas:
            resumen += "No hay carpetas seleccionadas.<br>"
        else:
            resumen += f"<b>Carpetas:</b> {', '.join([os.path.basename(c) for c in self.carpetas])}<br>"
        if self.destino:
            resumen += f"<b>Destino:</b> {self.destino}<br>"
        nombre_map = {0: 'Nombre fijo', 1: 'Fecha actual', 2: 'Fecha de edición'}
        resumen += f"<b>Nombre ZIP:</b> {nombre_map[self.combo_nombre.currentIndex()]}<br>"
        if self.checkbox_pass.isChecked():
            resumen += "<b>Contraseña:</b> Sí<br>"
        else:
            resumen += "<b>Contraseña:</b> No<br>"
        if self.checkbox_partes.isChecked():
            resumen += f"<b>Particionado:</b> Sí, {self.slider.value()} MB por parte<br>"
        else:
            resumen += "<b>Particionado:</b> No<br>"
        if self.checkbox_swiss.isChecked():
            resumen += "<b>Abrir SwissTransfer:</b> Sí<br>"
        else:
            resumen += "<b>Abrir SwissTransfer:</b> No<br>"
        self.label_resumen.setText(resumen)
    def comprimir(self):
        if not self.carpetas or not self.destino:
            QMessageBox.warning(self, "⚠️ Error", "Debes seleccionar al menos una carpeta y el destino.")
            return
        from core import comprimir_varias_carpetas_zip
        nombre_map = {0: 'nombre', 1: 'fecha', 2: 'editado'}
        nombre_auto = nombre_map[self.combo_nombre.currentIndex()]
        password = self.input_pass.text() if self.checkbox_pass.isChecked() else None
        split_size = self.slider.value() if self.checkbox_partes.isChecked() else None
        # Barra de progreso emergente
        from PySide6.QtWidgets import QProgressDialog
        self.progress_dialog = QProgressDialog("Comprimiendo...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Progreso de compresión")
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()
        QApplication.processEvents()
        try:
            partes = comprimir_varias_carpetas_zip(self.carpetas, self.destino, nombre_auto, password, split_size)
        except Exception as e:
            self.progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Ocurrió un error al comprimir:\n{e}")
            return
        self.progress_dialog.close()
        QMessageBox.information(self, "Completado", f"Se generaron {len(partes)} archivos ZIP/partes.")
        self.archivos_generados = partes
        if self.checkbox_swiss.isChecked():
            import webbrowser
            webbrowser.open('https://www.swisstransfer.com/es')

class DashboardUI(QWidget):
    """
    Clase principal del dashboard con tarjetas de funcionalidades.
    """
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.setWindowTitle(f"Flowbooster {APP_VERSION} - Dashboard")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(open("styles.qss").read())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header_layout = QVBoxLayout()
        
        titulo = QLabel("🎥 Flowbooster")
        titulo.setStyleSheet("font-size: 32px; font-weight: bold; color: #bb86fc;")
        titulo.setAlignment(Qt.AlignCenter)
        
        subtitulo = QLabel("Organiza tus proyectos audiovisuales con herramientas especializadas")
        subtitulo.setStyleSheet("font-size: 16px; color: #cccccc;")
        subtitulo.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(titulo)
        header_layout.addWidget(subtitulo)
        main_layout.addLayout(header_layout)
        
        # Área de tarjetas con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Widget contenedor de tarjetas
        tarjetas_widget = QWidget()
        tarjetas_layout = QGridLayout(tarjetas_widget)
        tarjetas_layout.setSpacing(20)
        tarjetas_layout.setAlignment(Qt.AlignCenter)
        
        # Definir las funcionalidades disponibles
        funcionalidades = [
            {
                "titulo": "Organizar por Tipo",
                "descripcion": "Clasifica archivos en carpetas por tipo: JPG, RAW, Videos. Ideal para proyectos fotográficos.",
                "icono": "📁",
                "color": "blue",
                "dialogo": OrganizadorPorTipoDialog
            },
            {
                "titulo": "Organizar por Fecha",
                "descripcion": "Organiza archivos por fecha de creación. Soporta EXIF y múltiples niveles: día, semana, mes, año.",
                "icono": "📅",
                "color": "green",
                "dialogo": OrganizadorPorFechaDialog
            },
            {
                "titulo": "Comparar y Emparejar",
                "descripcion": "Compara dos carpetas y mueve archivos sin pareja.",
                "icono": "🔗",
                "color": "purple",
                "dialogo": CompararEmparejarDialog
            },
            {
                "titulo": "Análisis de Proyecto",
                "descripcion": "Analiza el contenido de una carpeta y genera reportes detallados de archivos multimedia.",
                "icono": "📊",
                "color": "purple",
                "dialogo": None  # TODO: Implementar
            },
            {
                "titulo": "Limpieza de Archivos",
                "descripcion": "Encuentra y elimina archivos duplicados, temporales o innecesarios en tu proyecto.",
                "icono": "🧹",
                "color": "orange",
                "dialogo": None  # TODO: Implementar
            },
            {
                "titulo": "Conversión de Formatos",
                "descripcion": "Convierte archivos entre diferentes formatos de imagen y video de forma masiva.",
                "icono": "🔄",
                "color": "red",
                "dialogo": None  # TODO: Implementar
            },
            {
                "titulo": "Backup Automático",
                "descripcion": "Crea copias de seguridad automáticas de tus proyectos con compresión y verificación.",
                "icono": "💾",
                "color": "teal",
                "dialogo": None  # TODO: Implementar
            },
            {
                "titulo": "Comprimir y Particionar",
                "descripcion": "Comprime y particiona carpetas seleccionadas, y sube los archivos a SwissTransfer.",
                "icono": "🗜️",
                "color": "purple",
                "dialogo": ComprimirParticionarDialog
            }
        ]
        
        # Crear las tarjetas
        for i, func in enumerate(funcionalidades):
            row = i // 3
            col = i % 3
            
            tarjeta = TarjetaFuncionalidad(
                func["titulo"],
                func["descripcion"], 
                func["icono"],
                func["color"]
            )
            
            if func["dialogo"]:
                tarjeta.mousePressEvent = lambda event, dlg=func["dialogo"]: self.abrir_funcionalidad(dlg)
            
            tarjetas_layout.addWidget(tarjeta, row, col)
        
        scroll_area.setWidget(tarjetas_widget)
        main_layout.addWidget(scroll_area)
        
        # Footer
        footer = QLabel("Desarrollado con ❤️ por Felipe Hincapié | Caracol Aventurero")
        footer.setStyleSheet("font-size: 12px; color: #888888; text-align: center;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
    
    def abrir_funcionalidad(self, dialogo_class):
        """
        Abre el diálogo de la funcionalidad seleccionada.
        """
        dialogo = dialogo_class(self)
        dialogo.exec()

# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = DashboardUI()
    ventana.show()
    sys.exit(app.exec()) 
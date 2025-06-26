# -*- coding: utf-8 -*-

"""
Dashboard Principal de Flowbooster.

Este archivo define la interfaz principal con tarjetas para todas las
funcionalidades disponibles del programa.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QScrollArea, QSizePolicy, QSpacerItem, QDialog,
    QComboBox, QCheckBox, QFileDialog, QMessageBox, QProgressBar
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
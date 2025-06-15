# -*- coding: utf-8 -*-

"""
Módulo Principal de la Interfaz Gráfica de Flowbooster.

Este archivo define la clase OrganizadorUI, que construye y controla
todos los elementos visuales de la aplicación utilizando PySide6.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, 
    QProgressBar, QMessageBox, QCheckBox, QSpacerItem, QSizePolicy, QHBoxLayout, QFrame, QDialog
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QCursor, QMovie, QPixmap, QPainter, QColor, QBrush
import sys
import os
from core import procesar_proyecto, abrir_carpeta

APP_VERSION = "v1.0.0"

class FooterLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("footer")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.default_text = text
        self.hover_text = "Acerca de"
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(parent.width() if parent else 800)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    def enterEvent(self, event):
        self.setText(self.hover_text)
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.setText(self.default_text)
        super().leaveEvent(event)

class AcercaDeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de Flowbooster")
        self.setStyleSheet("background-color: #212121; color: #e0e0e0;")
        self.setFixedWidth(480)
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        # Imagen GIF animada circular con drop shadow
        image_path = os.path.abspath(os.path.join("img", "me.gif"))
        self.img_label = QLabel()
        self.img_label.setFixedSize(100, 100)
        self.img_label.setAlignment(Qt.AlignCenter)
        movie = QMovie(image_path)
        self.img_label.setMovie(movie)
        movie.start()
        self.img_label.paintEvent = lambda event, orig=self.img_label.paintEvent: self.paint_shadow(event, orig)
        layout.addWidget(self.img_label, alignment=Qt.AlignCenter)

        # Layout balanceado para explicación y redes
        hbox = QHBoxLayout()
        hbox.setSpacing(24)
        # Explicación
        expl = QLabel(f"<b>Flowbooster {APP_VERSION}</b><br>Organiza fotos y videos en carpetas limpias, con documentación automática.<br><span style='color:#bb86fc;'>Hecho en Python + PySide6</span>")
        expl.setWordWrap(True)
        expl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        expl.setStyleSheet("font-size:13px;")
        hbox.addWidget(expl, 1)
        # Redes con logos SVG mejorados
        redes = QLabel("""
        <b>Felipe Hincapié</b><br>
        <span style='color:#bb86fc;'>Caracol Aventurero</span><br>
        <div style='margin-top:8px;'>
            <a href='https://www.instagram.com/caracol.aventurero/' style='color: #bb86fc; text-decoration:none;' target='_blank'>
                <svg width='18' height='18' viewBox='0 0 24 24' style='vertical-align:middle; margin-right:4px;'>
                    <path fill='#bb86fc' d='M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z'/>
                </svg>Instagram
            </a>
            &nbsp;|&nbsp;
            <a href='https://github.com/Felipehincacode' style='color: #bb86fc; text-decoration:none;' target='_blank'>
                <svg width='18' height='18' viewBox='0 0 24 24' style='vertical-align:middle; margin-right:4px;'>
                    <path fill='#bb86fc' d='M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z'/>
                </svg>GitHub
            </a>
        </div>
        """)
        redes.setOpenExternalLinks(True)
        redes.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        redes.setStyleSheet("font-size:13px;")
        hbox.addWidget(redes, 1)
        layout.addLayout(hbox)

    def paint_shadow(self, event, orig_paint):
        # Dibuja un halo blanco detrás del GIF circular
        painter = QPainter(self.img_label)
        painter.setRenderHint(QPainter.Antialiasing)
        r = 50
        painter.setBrush(QBrush(QColor(255,255,255,60)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 100, 100)
        painter.setBrush(Qt.NoBrush)
        orig_paint(event)

class OrganizadorUI(QWidget):
    """
    Clase principal de la ventana de la aplicación.
    Hereda de QWidget y configura la interfaz de usuario.
    """
    def __init__(self):
        """Constructor de la clase. Se ejecuta al crear una nueva instancia."""
        super().__init__()

        # --- Configuración de la Ventana Principal ---
        self.setWindowTitle("Flowbooster")
        self.setMinimumSize(800, 700)  # Tamaño mínimo para evitar que los elementos se compriman
        self.setStyleSheet(open("styles.qss").read())  # Carga la hoja de estilos externa

        # Propiedades para almacenar las rutas seleccionadas por el usuario
        self.origen = ""
        self.destino = ""

        # --- Creación del Layout Principal ---
        # QVBoxLayout organiza los widgets verticalmente.
        main_layout = QVBoxLayout(self)  # 'self' lo asigna como el layout de esta ventana
        main_layout.setSpacing(20)  # Espacio entre widgets
        main_layout.setContentsMargins(50, 40, 50, 20)  # Márgenes (izquierda, arriba, derecha, abajo)
        main_layout.setAlignment(Qt.AlignTop)  # Alinea todo hacia la parte superior

        # --- Cabecera Clicable ---
        self.titulo = QPushButton("🎥 Flowbooster")
        self.titulo.setObjectName("titulo_btn")
        self.titulo.setProperty("class", "ClickableLabel")
        self.titulo.setCursor(QCursor(Qt.PointingHandCursor))
        self.titulo.setToolTip("Haz clic para ver información sobre el programa y el autor.")
        self.titulo.clicked.connect(self.mostrar_acerca)

        self.subtitulo = QPushButton("Organiza tus proyectos audiovisuales con un solo clic.")
        self.subtitulo.setObjectName("subtitulo_btn")
        self.subtitulo.setProperty("class", "ClickableLabel")
        self.subtitulo.setCursor(QCursor(Qt.PointingHandCursor))
        self.subtitulo.setToolTip("Haz clic para ver información sobre el programa y el autor.")
        self.subtitulo.clicked.connect(self.mostrar_acerca)

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.titulo, alignment=Qt.AlignCenter)
        header_layout.addWidget(self.subtitulo, alignment=Qt.AlignCenter)
        main_layout.addLayout(header_layout)

        # --- Sección 1: Selección de Carpetas ---
        main_layout.addSpacing(25)
        group1_layout = QVBoxLayout()
        group1_layout.setSpacing(15)
        
        instruccion1 = QLabel("1. Selecciona las carpetas")
        instruccion1.setToolTip("Selecciona primero la carpeta de origen (donde están tus archivos) y luego la de destino (donde se organizarán).")
        self.btn_origen = QPushButton("📂  Seleccionar Carpeta de Origen")
        self.btn_origen.setToolTip("Selecciona la carpeta donde están los archivos a organizar.")
        self.btn_destino = QPushButton("📁  Seleccionar Carpeta de Destino")
        self.btn_destino.setToolTip("Selecciona la carpeta donde se crearán las subcarpetas y se moverán/copiarán los archivos.")
        
        group1_layout.addWidget(instruccion1, alignment=Qt.AlignCenter)
        group1_layout.addWidget(self.btn_origen)
        group1_layout.addWidget(self.btn_destino)
        main_layout.addLayout(group1_layout)

        # --- Sección 2: Opciones (Centrado) ---
        main_layout.addSpacing(25)
        
        instruccion2 = QLabel("2. Elige tus preferencias")
        instruccion2.setToolTip("Configura cómo quieres que se organicen tus archivos y carpetas.")
        main_layout.addWidget(instruccion2, alignment=Qt.AlignCenter)
        
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 10, 0, 10)
        checkbox_layout.setSpacing(15)
        checkbox_layout.setAlignment(Qt.AlignCenter)

        self.checkbox_copiar = QCheckBox("Copiar archivos (en lugar de moverlos)")
        self.checkbox_copiar.setToolTip("Si está activado, los archivos se copiarán en la carpeta destino y permanecerán en la carpeta origen. Si está desactivado, los archivos se moverán.")
        self.checkbox_crear_todas = QCheckBox("Crear todas las carpetas (incluso vacías)")
        self.checkbox_crear_todas.setToolTip("Si está activado, se crearán todas las carpetas posibles (JPG, RAW, videos) aunque no haya archivos de ese tipo. Si está desactivado, solo se crearán las carpetas necesarias.")
        self.checkbox_readme = QCheckBox("Incluir un archivo README.md en cada carpeta")
        self.checkbox_readme.setToolTip("Si está activado, se generará un archivo README.md en cada carpeta creada, explicando qué tipo de archivos debe contener.")

        checkbox_layout.addWidget(self.checkbox_copiar)
        checkbox_layout.addWidget(self.checkbox_crear_todas)
        checkbox_layout.addWidget(self.checkbox_readme)
        main_layout.addWidget(checkbox_container, alignment=Qt.AlignCenter)

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        separator = QFrame()
        separator.setObjectName("separador")
        separator.setFrameShape(QFrame.HLine)  # Define la forma como línea horizontal
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # --- Sección 3: Acciones ---
        main_layout.addSpacing(15)
        self.btn_organizar = QPushButton("🚀  ORGANIZAR PROYECTO")
        self.btn_organizar.setObjectName("btn_organizar")
        self.btn_organizar.setToolTip("Haz clic para organizar los archivos según las opciones seleccionadas.")
        self.progreso = QProgressBar()
        self.progreso.setValue(0)
        self.progreso.setTextVisible(False)  # Oculta el texto de porcentaje
        self.progreso.setToolTip("Muestra el progreso del proceso de organización.")

        main_layout.addWidget(self.btn_organizar)
        main_layout.addWidget(self.progreso)
        
        # --- Footer Interactivo ---
        main_layout.addSpacing(15)
        self.footer = FooterLabel("Desarrollado con ❤️ por Felipe Hincapié")
        self.footer.setToolTip("Haz clic para ver información sobre el autor y el programa.")
        self.footer.mousePressEvent = lambda event: self.mostrar_acerca()
        main_layout.addWidget(self.footer, alignment=Qt.AlignCenter)
        
        # --- Conexiones de Señales ---
        self.btn_origen.clicked.connect(self.seleccionar_origen)
        self.btn_destino.clicked.connect(self.seleccionar_destino)
        self.btn_organizar.clicked.connect(self.organizar)


    def mostrar_acerca(self):
        dlg = AcercaDeDialog(self)
        dlg.exec()

    def seleccionar_origen(self):
        """Abre un diálogo para seleccionar la carpeta de origen."""
        carpeta = QFileDialog.getExistingDirectory(self, "📂 Seleccionar Carpeta Origen")
        if carpeta:  # Si el usuario selecciona una carpeta y no cancela
            self.origen = carpeta
            self.btn_origen.setText(f"📂 Origen: {os.path.basename(carpeta)}")

    def seleccionar_destino(self):
        """Abre un diálogo para seleccionar la carpeta de destino."""
        carpeta = QFileDialog.getExistingDirectory(self, "📁 Seleccionar Carpeta Destino")
        if carpeta:
            self.destino = carpeta
            self.btn_destino.setText(f"📁 Destino: {os.path.basename(carpeta)}")

    def organizar(self):
        """
        Función principal que se ejecuta al pulsar el botón "Organizar".
        Recopila todas las opciones y llama a la lógica del 'core'.
        """
        # Validaciones iniciales
        if not self.origen or not self.destino:
            QMessageBox.warning(self, "⚠️ Error", "Debes seleccionar ambas carpetas.")
            return

        total_archivos = len([a for a in os.listdir(self.origen) if os.path.isfile(os.path.join(self.origen, a))])
        
        # Recopila el estado de los checkboxes
        copiar = self.checkbox_copiar.isChecked()
        crear_todas = self.checkbox_crear_todas.isChecked()
        incluir_readme = self.checkbox_readme.isChecked()

        # Llama a la función principal del core y le pasa todos los parámetros
        log, tipo_proyecto = procesar_proyecto(self.origen, self.destino, copiar, crear_todas, incluir_readme)

        if tipo_proyecto == "vacio":
            QMessageBox.information(self, "ℹ️ Sin archivos", "No hay archivos para procesar en la carpeta origen.")
            return

        # Simulación de la barra de progreso
        self.progreso.setMaximum(total_archivos)
        for i in range(total_archivos + 1):
            # QTimer.singleShot es una forma de no bloquear la GUI mientras se actualiza
            QTimer.singleShot(i * 10, lambda i=i: self.progreso.setValue(i))

        # Mensaje de éxito final
        accion_str = "copiados" if copiar else "movidos"
        mensaje_exito = f"✅ ¡Éxito! {len(log)} archivos {accion_str}.\n"
        mensaje_exito += f"📂 Proyecto detectado como: **{tipo_proyecto}**.\n\n"
        mensaje_exito += "¿Quieres abrir la carpeta de destino?"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Proceso finalizado")
        msg_box.setText(mensaje_exito)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        # Si el usuario hace clic en "Sí", abre la carpeta
        if msg_box.exec() == QMessageBox.Yes:
            abrir_carpeta(self.destino)

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Crea la instancia de la aplicación
    ventana = OrganizadorUI()     # Crea la ventana principal
    ventana.show()                # Muestra la ventana
    sys.exit(app.exec())          # Inicia el bucle de eventos de la aplicación

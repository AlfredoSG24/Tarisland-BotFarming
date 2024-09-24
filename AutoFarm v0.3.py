import cv2
import numpy as np
import pyautogui
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from screeninfo import get_monitors  # Necesitamos instalar screeninfo
import threading
import keyboard  # Necesitamos instalar la biblioteca 'keyboard' para detectar teclas

# Variable global para controlar si el bot está corriendo
bot_activo = False
ventana_oculta = False


# Función para cargar la imagen
def cargar_imagen_interactiva():
    """
    Abre un diálogo para seleccionar la imagen y la carga.
    :return: Imagen cargada y su ruta, o None si no se selecciona.
    """
    ruta_imagen = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
    )

    if not ruta_imagen:
        messagebox.showwarning("No se seleccionó imagen", "Por favor selecciona una imagen.")
        return None, None

    imagen = cv2.imread(ruta_imagen)

    # Verificar si la imagen fue cargada correctamente
    if imagen is None:
        messagebox.showerror("Error",
                             f"La imagen '{ruta_imagen}' no se pudo cargar. Verifica que esté en el directorio correcto.")
        return None, None

    messagebox.showinfo("Imagen cargada", f"Imagen '{ruta_imagen}' cargada correctamente.")
    return imagen, ruta_imagen


# Función que realiza la acción de buscar la imagen, hacer dos clics y presionar la tecla F
def realizar_accion(template, template_width, template_height, monitor_region):
    """
    Busca la imagen en el monitor seleccionado, realiza dos clics y presiona F durante 15 segundos si se encuentra.
    :param monitor_region: Región del monitor donde buscar (x, y, width, height)
    """
    # Captura de pantalla solo en la región del monitor seleccionado
    screenshot = pyautogui.screenshot(region=monitor_region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Buscar la imagen en la captura de pantalla
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  # Ajusta según sea necesario
    loc = np.where(result >= threshold)

    # Si se encuentra la imagen, realiza dos clics y presiona la tecla F
    if len(loc[0]) > 0:
        for pt in zip(*loc[::-1]):  # Invierte las coordenadas (x, y)
            # Realiza 2 clics en la posición encontrada
            pyautogui.click(monitor_region[0] + pt[0] + template_width // 2,
                            monitor_region[1] + pt[1] + template_height // 2)
            pyautogui.click(monitor_region[0] + pt[0] + template_width // 2,
                            monitor_region[1] + pt[1] + template_height // 2)

            # Mantener la tecla F presionada durante 15 segundos
            pyautogui.keyDown('f')
            time.sleep(15)
            pyautogui.keyUp('f')
            return True
    return False


# Función principal del bot
def iniciar_bot(monitor_region):
    global bot_activo
    template, ruta_imagen = cargar_imagen_interactiva()

    if template is None:
        return

    template_height, template_width = template.shape[:2]

    # Ciclo infinito para realizar la acción en el monitor seleccionado
    while bot_activo:
        encontrado = realizar_accion(template, template_width, template_height, monitor_region)
        if encontrado:
            time.sleep(1)
        else:
            time.sleep(0.5)


# Función para iniciar el proceso del bot en un hilo separado
def iniciar_comparacion(monitor_region):
    global bot_activo
    if not bot_activo:
        bot_activo = True
        threading.Thread(target=iniciar_bot, args=(monitor_region,)).start()
        messagebox.showinfo("Bot iniciado", "La comparación de imágenes ha comenzado.")
    else:
        messagebox.showwarning("Bot en ejecución", "El bot ya está ejecutándose.")


# Función para detener el bot
def detener_bot():
    global bot_activo
    bot_activo = False
    messagebox.showinfo("Bot detenido", "El bot ha sido detenido.")


# Función para ocultar la ventana
def ocultar_ventana():
    global ventana_oculta
    root.withdraw()  # Ocultar ventana
    ventana_oculta = True


# Función para mostrar nuevamente la ventana cuando se presiona una tecla
def mostrar_ventana_al_presionar():
    global ventana_oculta
    while True:
        if keyboard.is_pressed('shift'):  # Tecla elegida para mostrar la ventana
            if ventana_oculta:
                root.deiconify()  # Mostrar ventana
                ventana_oculta = False
            time.sleep(1)  # Para evitar múltiples registros por una sola pulsación


# Función para seleccionar un monitor
def seleccionar_monitor():
    """
    Muestra una lista de los monitores conectados y devuelve las dimensiones del monitor seleccionado.
    """
    monitores = get_monitors()

    if not monitores:
        messagebox.showerror("Error", "No se detectaron monitores.")
        return None

    # Crear ventana para seleccionar el monitor
    ventana_seleccion = tk.Toplevel()
    ventana_seleccion.title("Seleccionar Monitor")

    label_instrucciones = tk.Label(ventana_seleccion, text="Selecciona el monitor:")
    label_instrucciones.pack(pady=10)

    # Variable para almacenar el monitor seleccionado
    monitor_seleccionado = tk.IntVar()

    for idx, monitor in enumerate(monitores):
        tk.Radiobutton(ventana_seleccion, text=f"Monitor {idx + 1}: {monitor.width}x{monitor.height}",
                       variable=monitor_seleccionado, value=idx).pack(anchor='w')

    def confirmar_monitor():
        idx = monitor_seleccionado.get()
        monitor = monitores[idx]
        monitor_region = (monitor.x, monitor.y, monitor.width, monitor.height)
        ventana_seleccion.destroy()
        messagebox.showinfo("Monitor seleccionado",
                            f"Monitor {idx + 1} seleccionado. Resolución: {monitor.width}x{monitor.height}")

        # Mostrar botones de iniciar y detener
        boton_iniciar = tk.Button(root, text="Iniciar Comparación", command=lambda: iniciar_comparacion(monitor_region),
                                  width=25, height=2)
        boton_iniciar.pack(pady=10)

        boton_detener = tk.Button(root, text="Detener Bot", command=detener_bot, width=25, height=2)
        boton_detener.pack(pady=10)

        # Botón para ocultar la ventana
        boton_ocultar = tk.Button(root, text="Ejecutar en segundo plano", command=ocultar_ventana, width=25, height=2)
        boton_ocultar.pack(pady=10)

    # Botón para confirmar selección
    boton_confirmar = tk.Button(ventana_seleccion, text="Confirmar", command=confirmar_monitor)
    boton_confirmar.pack(pady=10)


# Crear una interfaz gráfica para el botón
def iniciar_interfaz():
    global root
    root = tk.Tk()
    root.title("Farming Bot")

    # Botón para seleccionar el monitor
    seleccionar_monitor_btn = tk.Button(root, text="Seleccionar Monitor", command=seleccionar_monitor, width=25,
                                        height=2)
    seleccionar_monitor_btn.pack(pady=20)

    # Iniciar un hilo para escuchar la tecla para mostrar la ventana
    threading.Thread(target=mostrar_ventana_al_presionar, daemon=True).start()

    # Iniciar la ventana
    root.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()

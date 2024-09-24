import cv2
import numpy as np
import pyautogui
import time
import tkinter as tk
from tkinter import filedialog, messagebox


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


# Función principal del bot
def main():
    template, ruta_imagen = cargar_imagen_interactiva()

    if template is None:
        return

    template_height, template_width = template.shape[:2]

    while True:
        # Captura de pantalla
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Buscar la imagen en la captura de pantalla
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8  # Ajusta según sea necesario
        loc = np.where(result >= threshold)

        # Si se encuentra la imagen, haz algo (por ejemplo, clic)
        if len(loc[0]) > 0:
            for pt in zip(*loc[::-1]):  # Invierte las coordenadas (x, y)
                # Realiza 2 clics
                pyautogui.click(pt[0] + template_width // 2, pt[1] + template_height // 2)
                pyautogui.click(pt[0] + template_width // 2, pt[1] + template_height // 2)

                # Mantener la tecla F presionada durante 15 segundos
                pyautogui.keyDown('f')
                time.sleep(15)  # Mantener F presionada
                pyautogui.keyUp('f')

                time.sleep(1)  # Pausa de 1 segundo antes de la siguiente iteración

        time.sleep(0.5)  # Espera un poco antes de la siguiente captura


# Crear una interfaz gráfica para el botón
def iniciar_interfaz():
    root = tk.Tk()
    root.title("Farming Bot")

    # Botón para cargar la imagen
    cargar_imagen_btn = tk.Button(root, text="Cargar Imagen", command=main, width=25, height=2)
    cargar_imagen_btn.pack(pady=20)

    # Iniciar la ventana
    root.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()

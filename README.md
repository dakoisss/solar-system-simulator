# Simulador del sistema solar

**Made With ❤️ By Dakoi**

Simulador interactivo del sistema solar hecho con Python y Pygame. Muestra el
Sol y los ocho planetas con sus órbitas keplerianas, estelas y una cámara con  
zoom y escala lineal o logarítmica.  

## Requisitos

- Windows 10 u 11
- Python 3.12 recomendado
- `pip`

Pygame 2.6.1 se instala directamente con Python 3.12. Si tienes varias
versiones de Python instaladas, usa explícitamente Python 3.12 para crear el
entorno virtual.

## Instalación en Windows

Abre PowerShell en la carpeta del proyecto (`C:\Vscode\test`) y ejecuta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, permite scripts solo en la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

También puedes saltarte la activación y usar directamente el intérprete del
entorno virtual:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto, con el entorno activado:

```powershell
python .\main.py
```

O sin activar el entorno:

```powershell
& ".\.venv\Scripts\python.exe" ".\main.py"
```

En VS Code, selecciona `.venv\Scripts\python.exe` como intérprete de Python
(`Python: Select Interpreter`) para que Pylance encuentre Pygame.

## Controles

| Control | Acción |
| --- | --- |
| Rueda del ratón | Zoom centrado en el cursor |
| Arrastrar con botón central o derecho | Mover la vista |
| Espacio | Pausar o reanudar |
| `+` / `-` | Aumentar o reducir la velocidad |
| `T` | Mostrar u ocultar estelas |
| `L` | Alternar escala lineal o logarítmica |
| `O` | Mostrar u ocultar órbitas |
| `R` | Reiniciar la vista |
| `S` | Guardar una captura PNG |
| `Esc` | Salir |

## Estructura del proyecto

- `main.py`: ventana, controles, actualización y dibujo.
- `bodies.py`: datos planetarios y cálculos orbitales.
- `camera.py`: zoom, desplazamiento y transformaciones de coordenadas.
- `requirements.txt`: dependencias de Python.

## Comprobación orbital

Puedes ejecutar las verificaciones incluidas en `bodies.py` con:

```powershell
python .\bodies.py
```

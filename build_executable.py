import subprocess

def build_executable():
    command = [
        'pyinstaller',
        '--onefile',
        '--console',
        '--add-data', 'Captura_RFI_1.0.grc;.',
        '--add-data', 'GNU_Radio_installer.exe;.',
        '--add-data', 'Tratado_Datos.py;.',
        '--add-data', 'Visualizacion_Datos.py;.',
        'Medidor_RFI.py'
    ]
    subprocess.run(command, check=True)

if __name__ == '__main__':
    build_executable()

import os
import sys
import subprocess
import platform

def check_pdf(file_path):
    """Check if file exists and is a PDF."""
    if not os.path.exists(file_path):
        return False
    return file_path.lower().endswith('.pdf')

def get_file_size(file_path):
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def get_gs_binary():
    """Get the appropriate Ghostscript binary name based on OS and architecture."""
    system = platform.system().lower()
    if system == 'windows':
        gs_paths = [
            'C:\\Program Files\\gs\\gs10.04.0\\bin\\gswin64c.exe',
            'C:\\Program Files\\gs\\gs10.04\\bin\\gswin64c.exe'
        ]
        for path in gs_paths:
            if os.path.exists(path):
                return path
        return 'gswin64c.exe'
    return 'gs'

def check_ghostscript():
    """Verify Ghostscript installation and version."""
    try:
        gs_binary = get_gs_binary()
        version_check = subprocess.run([gs_binary, '--version'], 
                                     capture_output=True, 
                                     text=True)
        version = version_check.stdout.strip()
        
        if not version.startswith('10.04'):
            print(f"Advertencia: Se detectó Ghostscript versión {version}")
            print("Este script está optimizado para la versión 10.04")
            print("\nPara instalar Ghostscript 10.04:")
            if platform.system().lower() == 'windows':
                print("1. Descarga Ghostscript 10.04 desde https://ghostscript.com/releases/gsdnld.html")
                print("2. Instálalo en C:\\Program Files\\gs\\gs10.04.0")
                print("3. Añade C:\\Program Files\\gs\\gs10.04.0\\bin al PATH")
            return False
        return True
    except FileNotFoundError:
        print("Error: No se encontró Ghostscript")
        print("\nPor favor instala Ghostscript 10.04:")
        if platform.system().lower() == 'windows':
            print("1. Descarga Ghostscript 10.04 desde https://ghostscript.com/releases/gsdnld.html")
            print("2. Instálalo en C:\\Program Files\\gs\\gs10.04.0")
            print("3. Añade C:\\Program Files\\gs\\gs10.04.0\\bin al PATH")
        return False
    except Exception as e:
        print(f"Error verificando Ghostscript: {str(e)}")
        return False

def compress_pdf(input_path, output_path, quality='printer'):
    """
    Compress PDF using Ghostscript with different quality settings.
    quality options: 
    - 'printer' (300 dpi, alta calidad)
    - 'ebook' (150 dpi, calidad media)
    - 'screen' (72 dpi, menor calidad)
    """
    quality_settings = {
        'printer': '/printer',
        'ebook': '/ebook',
        'screen': '/screen'
    }
    
    gs_binary = get_gs_binary()
    gs_command = [
        gs_binary,
        '-dNOPAUSE',
        '-dBATCH',
        '-dQUIET',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.7',
        '-dPDFSETTINGS={}'.format(quality_settings.get(quality, '/printer')),
        '-dMaxSubsetPct=100',
        '-dSubsetFonts=true',
        '-dEmbedAllFonts=true',
        '-dAutoRotatePages=/None',
        '-dColorImageDownsampleType=/Bicubic',
        '-dColorImageResolution=300',  # Alta resolución para imágenes a color
        '-dGrayImageDownsampleType=/Bicubic',
        '-dGrayImageResolution=300',  # Alta resolución para imágenes en escala de grises
        '-dMonoImageDownsampleType=/Bicubic',
        '-dMonoImageResolution=300',  # Alta resolución para imágenes monocromáticas
        '-dDownsampleColorImages=false',  # Evitar reducción excesiva de calidad
        '-dDownsampleGrayImages=false',
        '-dDownsampleMonoImages=false',
        '-dColorConversionStrategy=/LeaveColorUnchanged',  # Mantener colores originales
        '-dAutoFilterColorImages=false',  # Evitar filtrado automático
        '-dAutoFilterGrayImages=false',
        '-dCompressPages=true',
        '-sOutputFile={}'.format(output_path),
        input_path
    ]
    
    try:
        subprocess.run(gs_command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error de Ghostscript: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python pdf_compressor.py <archivo.pdf>")
        print("\nEjemplo: python pdf_compressor.py documento.pdf")
        return

    if not check_ghostscript():
        return

    input_pdf = sys.argv[1]
    
    if not check_pdf(input_pdf):
        print("Error: El archivo no existe o no es un PDF")
        return

    output_pdf = os.path.splitext(input_pdf)[0] + "_compressed.pdf"
    
    original_size = get_file_size(input_pdf)
    print(f"Tamaño original: {original_size:.2f} MB")

    print("Comprimiendo PDF manteniendo alta calidad, por favor espere...")
    
    # Comenzar con la mejor calidad primero
    quality_levels = ['printer', 'ebook', 'screen']
    success = False
    
    for quality in quality_levels:
        print(f"\nProbando compresión nivel: {quality}")
        if compress_pdf(input_pdf, output_pdf, quality):
            compressed_size = get_file_size(output_pdf)
            reduction = ((original_size - compressed_size) / original_size * 100)
            
            if compressed_size < original_size:
                success = True
                print(f"\nCompresión exitosa con nivel {quality}:")
                print(f"Tamaño original: {original_size:.2f} MB")
                print(f"Tamaño comprimido: {compressed_size:.2f} MB")
                print(f"Reducción: {reduction:.1f}%")
                print(f"\nArchivo guardado como: {output_pdf}")
                break
            else:
                print("Intentando con siguiente nivel de compresión...")
                os.remove(output_pdf)
    
    if not success:
        print("\nNo se logró reducir el tamaño del archivo.")
        print("Esto puede deberse a que:")
        print("1. El PDF ya está altamente optimizado")
        print("2. El PDF contiene principalmente texto sin imágenes")
        print("3. Se utilizó previamente otra herramienta de compresión")

if __name__ == "__main__":
    main()
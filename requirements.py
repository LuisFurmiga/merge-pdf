"""Instala apenas as dependências usadas pelo aplicativo."""
import subprocess
import sys
from pathlib import Path

if __name__ == '__main__':
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(Path(__file__).with_name('requirements.txt'))])

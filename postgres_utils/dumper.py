import subprocess
import time
import os

# Configurações do banco de dados
host = os.getenv('host', "postgres")
port = os.getenv('port', 5432)
dbname = os.getenv('dbname', "postgres")
user = os.getenv('user', "postgres")
password = os.getenv('password', "postgres")
backup_file = os.getenv('db_backup', 'db_backup.sql')

# Função para medir o tempo de execução
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Tempo de execução: {elapsed_time:.2f} segundos")
        return result
    return wrapper

# Função para criar o dump do banco de dados
@measure_time
def create_backup():
    try:
        # Verifica o caminho do pg_dump
        pg_dump_path = subprocess.run(["which", "pg_dump"], check=True, text=True, capture_output=True).stdout.strip()
        if not pg_dump_path:
            raise FileNotFoundError("pg_dump não encontrado. Verifique se está instalado corretamente.")
        print(f"pg_dump encontrado em: {pg_dump_path}")

        # Comando para o pg_dump com SSL
        dump_cmd = [
            pg_dump_path,
            "-h", host,
            "-p", str(port),
            "-U", user,
            "-d", dbname,
            "-F", "c",  # Formato customizado
            "-b",  # Inclui blobs no backup
            "-v",  # Modo verboso
            "-f", backup_file
        ]

        # Configura a variável de ambiente para a senha
        env = {}
        env["PGPASSWORD"] = os.getenv('password', None)

        # Imprime o comando para depuração
        print(f"Executando comando: {' '.join(dump_cmd)}")

        # Executa o comando
        result = subprocess.run(dump_cmd, check=True, text=True, capture_output=True, env=env)
        print("Backup concluído com sucesso!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erro ao fazer o backup do banco de dados:")
        print(e.stderr)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Executa o backup
create_backup()
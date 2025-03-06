import subprocess
import time
import os

# Configurações do novo banco de dados (com valores padrão)
new_host = os.getenv('host', 'postgres')
new_port = os.getenv('port', '5432')
new_dbname = os.getenv('dbname', 'postgres')
new_user = os.getenv('user', 'postgres')
new_password = os.getenv('password', 'postgres')
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

# Função para executar comandos e verificar saída
def run_command(cmd, env=None):
    print(f"Executando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False, text=True, capture_output=True, env=env)
    if result.returncode != 0:
        print(f"Erro ao executar o comando: {' '.join(cmd)}")
        print(f"Código de retorno: {result.returncode}")
        print("Saída de erro (stderr):")
        print(result.stderr)
    else:
        print("Comando executado com sucesso!")
        print("Saída padrão (stdout):")
        print(result.stdout)
    return result

# Função para restaurar o dump do banco de dados
@measure_time
def restore_backup():
    try:
        # Encontra os caminhos para pg_restore e psql
        pg_restore_path = subprocess.run(["which", "pg_restore"], check=True, text=True, capture_output=True).stdout.strip()
        psql_path = subprocess.run(["which", "psql"], check=True, text=True, capture_output=True).stdout.strip()

        if not pg_restore_path:
            raise FileNotFoundError("pg_restore não encontrado. Verifique se está instalado corretamente.")
        if not psql_path:
            raise FileNotFoundError("psql não encontrado. Verifique se está instalado corretamente.")

        print(f"pg_restore encontrado em: {pg_restore_path}")
        print(f"psql encontrado em: {psql_path}")

        # Configura a variável de ambiente para a senha
        env = os.environ.copy()
        env['PGPASSWORD'] = new_password

        # Executa DROP DATABASE fora de um bloco de transação
        print(f"Dropping the database {new_dbname}...")
        drop_db_cmd = [
            psql_path,
            "-h", new_host,
            "-p", str(new_port),
            "-U", new_user,
            "-d", "postgres",  # Conecta-se ao banco de dados padrão 'postgres'
            "-c", f"DROP DATABASE IF EXISTS {new_dbname};"
        ]
        drop_db_result = run_command(drop_db_cmd, env)
        if drop_db_result.returncode != 0:
            return

        # Cria o banco de dados se não existir
        print(f"Creating the database {new_dbname} if it does not exist...")
        create_db_if_not_exists_cmd = [
            psql_path,
            "-h", new_host,
            "-p", str(new_port),
            "-U", new_user,
            "-d", "postgres",  # Conecta-se ao banco de dados padrão 'postgres'
            "-c", f"CREATE DATABASE {new_dbname} WITH OWNER = {new_user} ENCODING = 'UTF8' TEMPLATE = template0;"
        ]
        create_db_if_not_exists_result = run_command(create_db_if_not_exists_cmd, env)
        if create_db_if_not_exists_result.returncode != 0:
            return

        print(f"Banco de dados {new_dbname} limpo e recriado.")

        # Comando para o pg_restore com --no-owner e tratamento de erros aprimorado
        restore_cmd = [
            pg_restore_path,
            "-h", new_host,
            "-p", str(new_port),
            "-U", new_user,
            "-d", new_dbname,
            "-v",  # Modo verboso
            "--no-owner",  # Não define o proprietário
            backup_file
        ]

        restore_result = run_command(restore_cmd, env)
        if restore_result.returncode != 0:
            return

        print("Restauração concluída com sucesso!")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {e}")
        print("Saída de erro (stderr):")
        print(e.stderr)
        print("Código de retorno:", e.returncode)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Executa a restauração
restore_backup()

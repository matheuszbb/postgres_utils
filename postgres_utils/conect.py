import os
import psycopg2, psycopg2.extras
from contextlib import contextmanager

class DB:
    def __init__(self):
        try:
            self.conexao = psycopg2.connect(
                host=os.getenv('host', None),
                database=os.getenv('dbname', None),
                user=os.getenv('user', None),
                password=os.getenv('password', None),
                port=os.getenv('port', None),
            )
            print("Conexão com o banco de dados estabelecida com sucesso (SSL).")
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            exit()

    @contextmanager
    def get_db_cursor(self):
        cursor = self.conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()

    def execute_query(self, query, data=None):
        with self.get_db_cursor() as cursor:
            try:
                cursor.execute(query, data)
                self.conexao.commit()
                print(f"Comando executado com sucesso: {query}")  # Mensagem de sucesso para comandos
            except psycopg2.Error as e:
                self.conexao.rollback()  # Rollback em caso de erro
                print(f"Erro ao executar comando: {e}")

    def getter_query(self, query, data=None):
        with self.get_db_cursor() as cursor:
            try:
                cursor.execute(query, data)
                return cursor.fetchall()
            except psycopg2.Error as e:
                print(f"Erro ao executar consulta: {e}")
                return None  # Retorna None em caso de erro

    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        self.execute_query(query)
        print(f"Tabela '{table_name}' deletada (se existisse).")

    def list_tables(self):
        query = """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public';
        """
        return self.getter_query(query)
    
    def delete_data(self, table_name):
        query = f"DELETE FROM {table_name};"
        self.execute_query(query)
        print(f"Dados da tabela '{table_name}' deletados.")
    
    def remove_migration_entries(self, migrations):
        for migration in migrations:
            query = "DELETE FROM django_migrations WHERE app = %s AND name = %s;"
            app_name, migration_name = migration["app_name"], migration["migration_name"]
            self.execute_query(query, (app_name, migration_name))
            print(f"Entrada de migration '{migration}' removida do banco de dados.")
# Uso da classe DB
if __name__ == '__main__':
    db = DB()
    try:
        # Listar todas as tabelas
        tabelas = db.list_tables()
        print("Tabelas existentes antes da exclusão:")
        for tabela in tabelas:
            print(tabela['tablename'])

        # Verificação final das tabelas deletadas
        tabelas = db.list_tables()
        if not tabelas:
            print("Nenhuma tabela restante no banco de dados.")
        else:
            print("Tabelas restantes:", tabelas)

    except psycopg2.Error as e:
        print(f"Erro no uso do banco de dados: {e}")

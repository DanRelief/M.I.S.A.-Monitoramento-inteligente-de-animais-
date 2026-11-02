from src.infrastructure.database import get_db_connection


class RepositorioMedicacoes:

    def salvar(
        self,
        sessao_id: str,
        nome: str,
        quantidade: float | None,
        unidade: str | None,
        administrado_por: int,
        registrado_por: int,
        data_hora,
        observacao: str | None = None,
        dose_quantidade: str | None = None,
        animal_id: int | None = None,
    ) -> int:

        # Busca o animal_id vinculado à sessão caso não venha informado
        if animal_id is None:
            cmd_animal = "SELECT animal_id FROM sessoes_monitoramento WHERE id = %s"
            conexao_tmp = get_db_connection()
            cursor_tmp = conexao_tmp.cursor(dictionary=True)
            cursor_tmp.execute(cmd_animal, (sessao_id,))
            res = cursor_tmp.fetchone()
            cursor_tmp.close()
            conexao_tmp.close()
            if res:
                animal_id = res["animal_id"]
            else:
                raise ValueError(f"Sessão {sessao_id} não encontrada para associar a medicação.")

        if dose_quantidade is None:
            dose_quantidade = f"{quantidade} {unidade}" if quantidade is not None and unidade else "N/A"

        comando = """
            INSERT INTO historico_medicacoes (
                animal_id,
                sessao_id,
                administrado_por,
                registrado_por,
                medicamento,
                quantidade,
                unidade,
                dose_quantidade,
                observacao,
                data_hora
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        valores = (
            animal_id,
            sessao_id,
            administrado_por,
            registrado_por,
            nome,
            quantidade,
            unidade,
            dose_quantidade,
            observacao,
            data_hora,
        )

        conexao = None
        cursor = None

        try:
            conexao = get_db_connection()
            cursor = conexao.cursor()
            cursor.execute(comando, valores)
            conexao.commit()
            return cursor.lastrowid

        except Exception:
            if conexao is not None:
                conexao.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()

    def listar_por_sessao(
        self,
        id_sessao: str,
    ) -> list[dict]:

        comando = """
            SELECT
                m.id,
                m.sessao_id,
                m.medicamento AS nome,
                m.quantidade,
                m.unidade,
                m.administrado_por,
                m.registrado_por,
                u.nome AS nome_registrador,
                m.data_hora,
                m.observacao

            FROM historico_medicacoes m

            INNER JOIN usuarios u
                ON u.id = m.registrado_por

            WHERE m.sessao_id = %s

            ORDER BY
                m.data_hora ASC,
                m.id ASC
        """

        conexao = None
        cursor = None

        try:
            conexao = get_db_connection()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(comando, (id_sessao,))
            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()
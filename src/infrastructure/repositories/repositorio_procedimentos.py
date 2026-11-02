from src.infrastructure.database import (
    get_db_connection,
)


class RepositorioProcedimentos:

    def salvar(
        self,
        sessao_id: str,
        nome: str,
        executado_por: str | None,
        registrado_por: int,
        data_hora,
        observacao: str | None = None,
    ) -> int:

        # Alterado de 'procedimentos' para 'historico_procedimentos'
        comando = """
            INSERT INTO historico_procedimentos (
                animal_id,
                sessao_id,
                realizado_por,
                registrado_por,
                procedimento,
                descricao_detalhada,
                data_hora
            )
            SELECT 
                s.animal_id,
                %s, %s, %s, %s, %s, %s
            FROM sessoes_monitoramento s
            WHERE s.id = %s
        """

        # Nota: Caso sua tabela historico_procedimentos precise receber diretamente
        # o animal_id, ajuste conforme a assinatura do seu método. 
        # Mantendo compatível com a tabela unificada:
        comando_direto = """
            INSERT INTO historico_procedimentos (
                sessao_id,
                procedimento,
                realizado_por,
                registrado_por,
                data_hora,
                descricao_detalhada
            )
            VALUES (
                %s, %s, %s,
                %s, %s, %s
            )
        """

        valores = (
            sessao_id,
            nome,
            executado_por,
            registrado_por,
            data_hora,
            observacao,
        )

        conexao = None
        cursor = None

        try:
            conexao = get_db_connection()
            cursor = conexao.cursor()

            cursor.execute(
                comando_direto,
                valores,
            )

            conexao.commit()
            return cursor.lastrowid

        except Exception:
            if conexao is not None:
                conexao.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            if (
                conexao is not None
                and conexao.is_connected()
            ):
                conexao.close()

    def listar_por_sessao(
        self,
        id_sessao: str,
    ) -> list[dict]:

        comando = """
                SELECT
                    p.id,
                    p.sessao_id,
                    p.procedimento AS nome,
                    p.realizado_por AS executado_por,
                    p.registrado_por,
                    u.nome AS nome_registrador,
                    p.data_hora,
                    p.descricao_detalhada AS observacao

                FROM historico_procedimentos p

                INNER JOIN usuarios u
                    ON u.id = p.registrado_por

                WHERE p.sessao_id = %s

                ORDER BY
                    p.data_hora ASC,
                    p.id ASC
            """

        conexao = None
        cursor = None

        try:
            conexao = get_db_connection()
            cursor = conexao.cursor(
                dictionary=True
            )

            cursor.execute(
                comando,
                (id_sessao,),
            )

            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()

            if (
                conexao is not None
                and conexao.is_connected()
            ):
                conexao.close()
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from ...infrastructure.database import listar_alunos, deletar_aluno


class DialogGerenciarAlunos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar / Remover Alunos")
        self.setMinimumSize(600, 350)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Alunos Cadastrados no Sistema:</b>"))

        # Tabela de Alunos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome do Aluno", "Identificador (RA)"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.tabela)

        # Botão de Remoção (Vermelho)
        layout_botoes = QHBoxLayout()
        layout_botoes.addStretch()

        btn_remover = QPushButton("Remover Aluno Selecionado")
        btn_remover.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        btn_remover.clicked.connect(self._remover_aluno_selecionado)
        layout_botoes.addWidget(btn_remover)

        layout.addLayout(layout_botoes)
        self.setLayout(layout)

        self._carregar_alunos()

    def _carregar_alunos(self):
        """Busca os alunos cadastrados no banco MySQL e preenche a tabela."""
        self.alunos = listar_alunos()
        self.tabela.setRowCount(len(self.alunos))

        for i, aluno in enumerate(self.alunos):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(aluno["id"])))
            self.tabela.setItem(i, 1, QTableWidgetItem(aluno["nome"]))
            self.tabela.setItem(i, 2, QTableWidgetItem(str(aluno["identificador"])))

    def _remover_aluno_selecionado(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um aluno na tabela para remover.")
            return

        aluno = self.alunos[row]

        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja remover o aluno '{aluno['nome']}' (RA: {aluno['identificador']})?\n\n"
            "Atenção: Se o aluno tiver animais atribuídos a ele, a remoção será impedida.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if resposta == QMessageBox.StandardButton.Yes:
            sucesso, mensagem = deletar_aluno(aluno["id"])
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self._carregar_alunos()  # Recarrega a tabela imediatamente
            else:
                QMessageBox.warning(self, "Erro", mensagem)
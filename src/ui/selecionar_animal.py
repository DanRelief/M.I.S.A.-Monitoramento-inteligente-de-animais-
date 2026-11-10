from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, Signal
from ..infrastructure.database import listar_animais, deletar_animal


class DialogSelecionarAnimal(QDialog):
    animal_selecionado = Signal(dict, bool)  # (dados_animal, e_proprietario)

    def __init__(self, usuario_logado: dict, parent=None):
        super().__init__(parent)
        self.usuario_logado = usuario_logado
        self.setWindowTitle("Selecionar Animal para Monitorar")
        self.setMinimumSize(750, 420)

        # Normaliza o papel do usuário logado
        papel = self.usuario_logado.get("papel") or self.usuario_logado.get("role") or ""
        self.is_teacher = str(papel).strip().lower() in ["teacher", "docente", "professor", "admin"]

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Selecione um animal cadastrado na rede:"))

        # Tabela de Animais
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Espécie", "Estado", "Procedimento", "Responsável"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.tabela)

        # Layout dos botões inferiores
        layout_botoes = QHBoxLayout()
        
        # Botão de Remover (Fixo no layout, visível apenas para docentes)
        self.btn_deletar = QPushButton("Remover Animal")
        self.btn_deletar.setStyleSheet("""
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
        self.btn_deletar.clicked.connect(self._tratar_clique_deletar)
        self.btn_deletar.setVisible(self.is_teacher)  # Oculta para alunos
        layout_botoes.addWidget(self.btn_deletar)

        layout_botoes.addStretch()

        # Botão de Monitorar
        self.btn_monitorar = QPushButton("Iniciar Monitoramento")
        self.btn_monitorar.setStyleSheet("""
            QPushButton {
                background-color: #287a55;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #216746;
            }
        """)
        self.btn_monitorar.clicked.connect(self._tratar_clique_monitorar)
        layout_botoes.addWidget(self.btn_monitorar)

        layout.addLayout(layout_botoes)
        self.setLayout(layout)

        self._carregar_dados()

    def _carregar_dados(self):
        """Carrega e atualiza a lista de animais na tabela."""
        self.animais = listar_animais()
        self.tabela.setRowCount(len(self.animais))

        for i, a in enumerate(self.animais):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(a["id"])))
            self.tabela.setItem(i, 1, QTableWidgetItem(a["nome"]))
            self.tabela.setItem(i, 2, QTableWidgetItem(a["especie"]))
            self.tabela.setItem(i, 3, QTableWidgetItem(a["estado_clinico"]))
            self.tabela.setItem(i, 4, QTableWidgetItem(a["procedimento"]))
            self.tabela.setItem(i, 5, QTableWidgetItem(a["nome_responsavel"]))

    def _tratar_clique_monitorar(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um animal na tabela antes de prosseguir.")
            return

        animal = self.animais[row]
        self._confirmar_selecao(animal)

    def _tratar_clique_deletar(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um animal na tabela para remover.")
            return

        animal = self.animais[row]
        self._remover_animal(animal)

    def _confirmar_selecao(self, animal: dict):
        """Emite o sinal e fecha a janela para iniciar a sessão."""
        e_proprietario = (animal["responsavel_aplicacao"] == self.usuario_logado.get("id"))
        self.animal_selecionado.emit(animal, e_proprietario)
        self.accept()

    def _remover_animal(self, animal: dict):
        """Executa a remoção do animal após confirmação (exclusivo docente)."""
        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja remover o animal '{animal['nome']}' (ID: {animal['id']})?\n\n"
            "Esta ação apagará todo o histórico de monitoramento e medicações associados!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if resposta == QMessageBox.StandardButton.Yes:
            sucesso, mensagem = deletar_animal(animal["id"])
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self._carregar_dados()  # Atualiza a tabela imediatamente
            else:
                QMessageBox.warning(self, "Erro", mensagem)
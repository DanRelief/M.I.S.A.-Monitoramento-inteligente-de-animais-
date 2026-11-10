USE misa;

-- Desativa a trava de Safe Updates temporariamente para permitir os UPDATEs da migration
SET SQL_SAFE_UPDATES = 0;
SET @dbname = DATABASE();

-- ============================================================================
-- 1. MIGRAÇÃO: HISTÓRICO DE PROCEDIMENTOS
-- ============================================================================
SET @tablename = "historico_procedimentos";

-- Adiciona sessao_id se não existir (evita erro 1060)
SET @columnname = "sessao_id";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_procedimentos ADD COLUMN sessao_id VARCHAR(36) NULL AFTER animal_id;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Adiciona registrado_por se não existir
SET @columnname = "registrado_por";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_procedimentos ADD COLUMN registrado_por INT NULL AFTER realizado_por;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Preenche registros nulos de registrado_por com o valor original de realizado_por
UPDATE historico_procedimentos
SET registrado_por = realizado_por
WHERE registrado_por IS NULL;

-- Modifica registrado_por para NOT NULL
ALTER TABLE historico_procedimentos
MODIFY COLUMN registrado_por INT NOT NULL;

-- Adiciona FK sessao_id se não existir
SET @constraintname = "fk_hist_proc_sessao";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_procedimentos ADD CONSTRAINT fk_hist_proc_sessao FOREIGN KEY (sessao_id) REFERENCES sessoes_monitoramento(id) ON DELETE SET NULL ON UPDATE CASCADE;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Adiciona FK registrado_por se não existir
SET @constraintname = "fk_hist_proc_registrador";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_procedimentos ADD CONSTRAINT fk_hist_proc_registrador FOREIGN KEY (registrado_por) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE CASCADE;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;


-- ============================================================================
-- 2. MIGRAÇÃO: HISTÓRICO DE MEDICAÇÕES
-- ============================================================================
SET @tablename = "historico_medicacoes";

-- Adiciona sessao_id se não existir
SET @columnname = "sessao_id";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_medicacoes ADD COLUMN sessao_id VARCHAR(36) NULL AFTER animal_id;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Adiciona registrado_por se não existir
SET @columnname = "registrado_por";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_medicacoes ADD COLUMN registrado_por INT NULL AFTER administrado_por;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Adiciona quantidade se não existir
SET @columnname = "quantidade";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_medicacoes ADD COLUMN quantidade DOUBLE NULL AFTER medicamento;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Adiciona unidade se não existir
SET @columnname = "unidade";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_medicacoes ADD COLUMN unidade VARCHAR(30) NULL AFTER quantidade;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Preenche registros nulos de registrado_por com o valor original de administrado_por
UPDATE historico_medicacoes
SET registrado_por = administrado_por
WHERE registrado_por IS NULL;

-- Modifica registrado_por para NOT NULL
ALTER TABLE historico_medicacoes
MODIFY COLUMN registrado_por INT NOT NULL;

-- Adiciona FK sessao_id se não existir
SET @constraintname = "fk_hist_med_sessao";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_medicacoes ADD CONSTRAINT fk_hist_med_sessao FOREIGN KEY (sessao_id) REFERENCES sessoes_monitoramento(id) ON DELETE SET NULL ON UPDATE CASCADE;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Adiciona FK registrado_por se não existir
SET @constraintname = "fk_hist_med_registrador";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) > 0,
  "SELECT 1",
  "ALTER TABLE historico_medicacoes ADD CONSTRAINT fk_hist_med_registrador FOREIGN KEY (registrado_por) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE CASCADE;"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;


-- ============================================================================
-- 3. CRIAÇÃO DE ÍNDICES (COM VERIFICAÇÃO DE EXISTÊNCIA)
-- ============================================================================
SET @tablename = "historico_procedimentos";
SET @indexname = "idx_hist_proc_sessao_data";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  "SELECT 1",
  "CREATE INDEX idx_hist_proc_sessao_data ON historico_procedimentos (sessao_id, data_hora);"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @tablename = "historico_medicacoes";
SET @indexname = "idx_hist_med_sessao_data";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  "SELECT 1",
  "CREATE INDEX idx_hist_med_sessao_data ON historico_medicacoes (sessao_id, data_hora);"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @tablename = "sessoes_monitoramento";
SET @indexname = "idx_sessao_animal_inicio";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  "SELECT 1",
  "CREATE INDEX idx_sessao_animal_inicio ON sessoes_monitoramento (animal_id, data_hora_inicio);"
));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Reativa a trava de segurança de atualizações
SET SQL_SAFE_UPDATES = 1;
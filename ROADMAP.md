# 📍 CallSplitter-Cleaner: Roadmap Técnico

Este ficheiro serve como guia técnico para o desenvolvimento contínuo do projeto CallSplitter-Cleaner na branch `enhancement`.

---

## ✅ Fase Atual (v3.x)
**Objetivo:** Filtrar chamadas reais com base em padrões de fala e melhorar a estrutura do pipeline.

### 🔧 Funcionalidades implementadas
- [x] Divisão de áudio por silêncio
- [x] Transcrição com Whisper (modelo base)
- [x] Filtro por frases-chave ("posso ser útil", etc.)
- [x] Sistema de pontuação e confiança
- [x] Logs por chamada
- [x] Armazenamento opcional de suspeitas

---

## 🛠️ Próxima Fase: Regras Adaptadas ao Estilo do Vitor

### 🎯 Objetivo
Criar regras mais robustas baseadas nas chamadas reais do Vitor Varela.

### 📌 Tarefas
- [ ] Subir 5–10 chamadas reais para análise
- [ ] Extrair expressões reais de abertura e encerramento
- [ ] Criar regex ou regras de validação baseadas nas frases reais
- [ ] Substituir heurística atual por `rules.json` ou função dinâmica

---

## 🔄 Refatoração e Performance (Parcialmente Concluído)

### 📌 Tarefas
- [x] Processamento por blocos (implementado com divisão por silêncio)
- [ ] Barra de progresso no terminal
- [x] Logging de tempo e consumo de recursos (logs básicos implementados)
- [x] Exportar relatórios por ficheiro (.json) (implementado em v3.0)

---

## 📦 Fase de Lote e Automação

### 📌 Tarefas
- [x] Processar pastas com 30+ ficheiros automaticamente (implementado em v3.0)
- [x] Suporte a múltiplos formatos (.wav, .mp3) (implementado em v3.0)
- [ ] Remoção de duplicados ou ficheiros inválidos
- [x] Exportar estatísticas gerais em `.csv` ou `.json` (logs em .json implementados)

---

## 📈 Métricas Futuras (Análise)

### 📌 Ideias
- [ ] Duração falada vs. duração total
- [ ] Nº de palavras do operador vs. cliente
- [ ] Nível médio de confiança por chamada
- [ ] Detectar ausência de "encerramento profissional"

---

## 🤖 Fase Final: Treinamento Personalizado (opcional)
- [ ] Usar as transcrições reais para treinar embedding personalizado
- [ ] Criar classificador leve (SVM ou Similarity Model)
- [ ] Avaliar chamadas automaticamente com scoring personalizado

---

Feito com ⚙️ por Vitor Varela, rumo ao CallScan completo 💼📞

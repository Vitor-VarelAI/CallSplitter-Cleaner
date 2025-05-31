# 📍 CallSplitter-Cleaner: Roadmap Técnico

Este ficheiro serve como guia técnico para o desenvolvimento contínuo do projeto CallSplitter-Cleaner na branch `enhancement`.

---

## ✅ Fase Atual (v4.0)
**Objetivo:** Processamento robusto de lote com configuração flexível e tratamento de erros aprimorado.

### 🚀 Novas Funcionalidades
- [x] Configuração via linha de comando (argparse)
- [x] Caminhos personalizáveis (input/output/logs)
- [x] Detecção de silêncio ajustável
- [x] Tratamento de erros robusto
- [x] Nomeação de arquivos sem colisão
- [x] Logs estruturados (arquivo + console)

### 🔧 Funcionalidades implementadas
- [x] Divisão de áudio por silêncio
- [x] Transcrição com Whisper (modelo base)
- [x] Filtro por frases-chave ("posso ser útil", etc.)
- [x] Sistema de pontuação e confiança
- [x] Logs detalhados por chamada
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

## 🔄 Refatoração e Performance (Concluído v4.0)

### ✅ Melhorias Implementadas
- [x] Processamento por blocos otimizado
- [x] Sistema de logging unificado (arquivo + console)
- [x] Tratamento de erros robusto
- [x] Exportação de relatórios em .json
- [x] Verificação de dependências (FFmpeg)

### 📊 Próximas Melhorias
- [ ] Barra de progresso no terminal
- [ ] Estatísticas de desempenho detalhadas

---

## 📦 Fase de Lote e Automação (Concluído v4.0)

### ✅ Funcionalidades Implementadas
- [x] Processamento em lote de múltiplos formatos
- [x] Nomeação automática sem colisão
- [x] Logs estruturados e arquivados
- [x] Exportação de estatísticas em .json

### 🔍 Próximos Passos
- [ ] Detecção automática de duplicados
- [ ] Processamento incremental (apenas novos arquivos)

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

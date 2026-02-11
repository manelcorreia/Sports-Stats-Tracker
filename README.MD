# PROJETO: PAREDE FC STATS TRACKER
ALUNO: MANUEL CORREIA
Nº 2403849
---
Este projeto é uma aplicação de linha de comandos (CLI) desenvolvida em Python para a gestão desportiva e análise estatística da equipa de Hóquei em Patins do Parede FC

A aplicação permite que a equipa técnica registe eventos do jogo em tempo real (golos, assistências, defesas, cartões, etc) e consultar estatísticas detalhadas através de uma interface visual moderna. O sistema garante a persistência de dados entre sessões e implementa conceitos avançados de Programação Orientada a Objetos. 

---
## PRINCIPAIS FUNCIONALIDADES
- Gestão de Plantel: Listagem de jogadores com distinção entre Guarda-Redes e Jogadores de Campo.
- Live Match Tracking: Registo Intuitivo de eventos durante o jogo (Golos, assistências, bolas paradas, disciplina, etc).
- Interface Visual: Utilização da biblioteca Rich para apresentar tabelas de consulta estatística formatadas, painéis coloridos e menus interativos.
- Estatísticas Automáticas: Cálculo de totais (Vitórias/Derrotas, Golos Marcados/Sofridos) e métricas individuais.
- Persistência de dados: Salvaguarda automática de todo o histórico em ficheiro JSON.
- Arquitetura Técnica: Implementação de Herança Múltipla e Mixins para modularidade do código.

---
## COMO EXECUTAR
1. Certifique-se de que a pasta '.venv' está presente.
2. Execute o ficheiro principal: 
```bash
python Projeto_StatsTracker.py
```

---
## NOTA TÉCNICA
O projeto inclui a pasta '.venv' conforme as instruções do forúm de dúvidas da cadeira.
Caso ocorra algum erro de compatibilidade, inclui também o ficheiro 'requirements.txt'.
Para reinstalar as dependências, pode usar: 
```bash
pip install -r requirements.txt
``` 

--- 
## ⚠️ Nota sobre a visualização (Cores do Rich)
Este projeto utiliza a biblioteca `Rich` para interfaces coloridas
Caso execute o código dentro do **PyCharm**, por favor ative a opção:
`Emulate terminal in output console` nas configurações de execução (Run Configuration).

Se executar pelo **Terminal do Windows/CMD**, as cores funcionam automaticamente sem configuração extra.

---
## ⚠️ Nota sobre a Persistência de Dados
O sistema de persistência (JSON) foi atualizado recentemente para corrigir a serialização de objetos (mudança de chaves de variáveis).
O ficheiro de dados atual (`dados_equipa.json`) mantém o histórico antigo, mas algumas estatísticas acumuladas (como Defesas e Golos Sofridos) só começarão a contar corretamente a partir dos novos jogos registados nesta versão final.
# Snake — Project Constitution

## Core Principles

### I. Núcleo Puro, Casca Fina (NON-NEGOTIABLE)

Todas as regras de jogo — grade, cobra, comida, colisão, pontuação, velocidade — vivem em um módulo independente de renderização, testável sem interface. Renderização e entrada são adaptadores finos sobre o núcleo.

- O núcleo de lógica de jogo (`game.core`) deve ser 100% funcional/imutável — sem efeitos colaterais, sem I/O, sem dependências de frameworks ou bibliotecas gráficas.
- Renderização (`render.*`) e entrada (`input.*`) são módulos de adaptador que convertem estados puros em pixels/events e conversões de events em comandos puros.
- Testes unitários do núcleo rodam sem GUI, sem terminal, sem X11 — apenas Python e `pytest`.

### II. Test-First (NON-NEGOTIABLE)

Toda mudança de regra começa com um `pytest` que falha.

- Ciclo estritamente Red → Green → Refactor.
- Nada de produção é commitado até o teste correspondente estar verde.
- Regras de jogo → testes unitários puros (fake state).
- Regras de render/entrada → testes de integração mínima (fake event loop).

### III. Simulação Determinística

RNG injetado e seedado, para que qualquer estado de jogo seja reproduzível.

- Fonte de aleatoriedade: instância de `random.Random(seed)` injetada no construtor do game state.
- Spawn de comida, velocidade incremental, e qualquer outra não-determinismia passam pelo RNG injetado.
- Dado o mesmo seed + sequência de inputs, o estado final é idêntico em cada execução — testável via `pytest`.
- Sem `random.seed()` global, sem `time.time()`, sem `os.urandom()` no núcleo.

### IV. Sem Complexidade Prematura

YAGNI em cada linha.

- Nenhuma abstração extra até que um caso de uso real a exija.
- Sem classes base, sem estratégias, sem observers — antes de existir o requisito, é especulação.
- Cada função/módulo existe para resolver algo já especificado no `spec.md`.
- Refatoração é permitida e incentivada; antecipação não.

### V. Jogável em Todo Checkpoint

Cada fatia de implementação termina em um estado executável.

- Ao final de cada task do plano, o jogo deve estar funcional — mesmo que com output ASCII no terminal.
- Nenhum estado quebrado é commitado: a cada PR, `pytest` passa e um loop mínimo roda.
- Progresso incremental válido: (1) core movement → (2) food + score → (3) collision + game over → (4) terminal render.

## Governance

Esta constituição é a regra máxima do projeto. Qualquer divergência entre esta e outros documentos (spec, plan, tasks) é resolvida em favor desta. Alterações exigem revisão explícita do autor e registro de motivação em PR dedicado.

**Version**: 1.0.0 | **Ratified**: 2026-11-12 | **Last Amended**: 2026-11-12

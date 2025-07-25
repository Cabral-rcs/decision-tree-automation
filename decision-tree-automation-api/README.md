## Modo Sandbox (Seguro para Testes)

- Para garantir que nenhum dado real seja afetado, defina a variável de ambiente `SANDBOX_MODE=1` ao rodar o backend.
- O banco de dados será criado em memória (SQLite), descartado ao reiniciar.
- Nenhuma integração real com Telegram ou sistemas externos será feita.

## Observações
- Nunca rode o backend sem a variável `SANDBOX_MODE=1` em ambiente de testes.
- Não há risco de afetar o sistema operacional ou dados institucionais. 
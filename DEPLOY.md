# Deploy: GitHub + Vercel + Turso

Siga nessa ordem — cada etapa depende da anterior.

## 1. Turso (banco de dados)

1. Instale a CLI do Turso:
   ```powershell
   curl -sSfL https://get.tur.so/install.sh | bash
   ```
   (No Windows, use WSL ou o instalador via `scoop install turso` — veja https://docs.turso.tech/cli/installation)

2. Crie uma conta e faça login:
   ```
   turso auth signup
   ```

3. Crie o banco:
   ```
   turso db create eventos-energisa
   ```

4. Pegue a URL de conexão:
   ```
   turso db show eventos-energisa --url
   ```
   Isso devolve algo como `libsql://eventos-energisa-seuusuario.turso.io` — guarde esse valor, é o `TURSO_DATABASE_URL`.

5. Gere um token de autenticação:
   ```
   turso db tokens create eventos-energisa
   ```
   Guarde esse valor, é o `TURSO_AUTH_TOKEN`.

**Importante**: o banco Turso começa **vazio** — sem tabelas, sem usuário admin. As tabelas são criadas automaticamente na primeira vez que o app conectar nele (mesma lógica do `init_db()` que já roda hoje no SQLite local).

## 2. GitHub

1. Crie um repositório novo no GitHub (pode ser privado).
2. Na pasta do projeto, no terminal:
   ```powershell
   git init
   git add .
   git commit -m "Primeira versão"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
   git push -u origin main
   ```

**Antes de rodar isso**, confira que o `.gitignore` está na pasta (ele impede que `instance/energisa.db`, `uploads/` e outros arquivos locais/sensíveis subam pro GitHub por engano).

## 3. Vercel

1. Crie uma conta em vercel.com (pode entrar direto com a conta do GitHub).
2. No painel da Vercel, clique em "Add New" → "Project" e escolha o repositório que você acabou de subir.
3. **Antes de clicar em Deploy**, configure as variáveis de ambiente (Project Settings → Environment Variables):

   | Nome | Valor |
   |---|---|
   | `SECRET_KEY` | Gere uma com `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `TURSO_DATABASE_URL` | O valor que você pegou no passo 1.4 |
   | `TURSO_AUTH_TOKEN` | O valor que você pegou no passo 1.5 |

4. Crie um **Blob Store** pro armazenamento de evidências: no painel do projeto, vá em "Storage" → "Create Database" → "Blob". A Vercel injeta o `BLOB_READ_WRITE_TOKEN` sozinha nas variáveis de ambiente do projeto — não precisa configurar manualmente.

5. O **Cron Job** já está configurado no `vercel.json` (roda às 04:00 e 15:00 UTC, que equivale a 01:00 e 12:00 de Brasília). A Vercel cria automaticamente a variável `CRON_SECRET` e a usa pra autenticar as chamadas — também não precisa configurar nada manualmente.

6. Clique em "Deploy".

## 4. Depois do primeiro deploy

- Acesse a URL que a Vercel te deu (algo como `seu-projeto.vercel.app`).
- Faça login com `admin@energisa.com.br` / senha `123456` — o app cria esse usuário sozinho na primeira conexão com o banco vazio.
- **Troque essa senha imediatamente** (o app já força isso no primeiro login).
- Teste o cadastro de um evento e uma inscrição, pra confirmar que a escrita no Turso está funcionando.
- Teste o upload de uma evidência, pra confirmar que o Vercel Blob está funcionando.

## Diferenças de comportamento entre local e produção

| Recurso | Local (seu PC) | Produção (Vercel) |
|---|---|---|
| Banco de dados | SQLite (`instance/energisa.db`) | Turso |
| Evidências | Pasta `uploads/` | Vercel Blob |
| Atualização automática de eventos | APScheduler (roda dentro do processo) | Vercel Cron chamando `/api/cron/update-events` |
| Templates HTML | Escritos em `templates/` | Servidos direto da memória (a Vercel não permite gravar disco) |

## Atualizações futuras

Depois desse primeiro deploy, qualquer novo `git push` pra branch `main` faz a Vercel re-publicar automaticamente — não precisa repetir esse guia inteiro, só o passo 2 (commit + push).

## ⚠️ Nota sobre `sqlalchemy-libsql` no Windows

O pacote que conecta ao Turso (`sqlalchemy-libsql`) **oficialmente só suporta Linux e macOS**. Isso não afeta a Vercel (que roda Linux), mas se você tentar instalar `pip install -r requirements.txt` no seu PC Windows, essa linha pode falhar. Nesse caso, tudo bem — localmente você não precisa dela mesmo, já que o app usa SQLite local por padrão quando `TURSO_DATABASE_URL` não está definida. Se o `pip install` falhar por causa desse pacote, comente a linha `sqlalchemy-libsql` no `requirements.txt` local (sem apagar do arquivo que vai pro GitHub/Vercel).

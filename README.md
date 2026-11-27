# IBF — SQLite

## Arquitetura
Django + SQLite. O computador Windows servidor executa a aplicação; os demais computadores acessam pelo navegador na rede local. O arquivo `data/gestao_igreja.sqlite3` fica no disco local do servidor.

## Concorrência
SQLite permite vários leitores, mas somente um escritor por vez. WAL e timeout de 20 segundos estão configurados para melhorar a convivência entre 3 a 5 usuários com movimentação moderada. Se houver bloqueios frequentes ou crescimento, migraremos para PostgreSQL.

**Não compartilhe o arquivo SQLite para acesso direto pelos clientes.** Somente o Django no servidor deve acessar o banco.

## Instalação
1. Extraia para `C:\IBF`.
2. Abra CMD nessa pasta e execute:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

3. Edite `.env` e troque `DJANGO_SECRET_KEY` por uma chave longa e aleatória.
4. Execute:

```bat
python manage.py check
python manage.py migrate
python manage.py createsuperuser
```

5. Teste no servidor:

```bat
python manage.py runserver 127.0.0.1:8000
```

Acesse `http://127.0.0.1:8000/admin/`.

## Teste na rede local
Descubra o IPv4 com `ipconfig`, adicione-o em `DJANGO_ALLOWED_HOSTS` no `.env`, por exemplo `localhost,127.0.0.1,192.168.1.50`. Para teste, execute `python manage.py runserver 0.0.0.0:8000`, libere TCP 8000 no Firewall do Windows apenas para a rede privada e acesse `http://IP-DO-SERVIDOR:8000/`.

`runserver` é apenas para desenvolvimento. Antes do uso real, configurar servidor WSGI apropriado, inicialização automática, firewall restrito, backups consistentes e teste de restauração. Não exponha o sistema à internet.

## Backup
Não copie apenas o arquivo principal enquanto o sistema estiver em uso: no modo WAL podem existir arquivos auxiliares `-wal` e `-shm`. A rotina definitiva usará backup consistente do SQLite, cópia para outro dispositivo e teste de restauração.

Os módulos estão estruturados, mas os modelos e telas de pessoas, financeiro e relatórios serão construídos nas próximas etapas.

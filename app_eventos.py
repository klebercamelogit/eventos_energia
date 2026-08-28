import os
import uuid
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler

LOGO_BASE64 = "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"

app = Flask(__name__)

# SECRET_KEY: nunca deixar hardcoded quando o código vai pro GitHub — qualquer pessoa com
# acesso ao repositório poderia forjar sessões de login sabendo essa chave.
# Em produção (Vercel), defina a variável de ambiente SECRET_KEY.
# Localmente, se não definir, usa uma chave de desenvolvimento (não usar em produção).
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-nao-usar-em-producao-2026')

# Detecta se está rodando no Vercel (a Vercel define VERCEL=1 automaticamente)
IS_VERCEL = bool(os.environ.get('VERCEL'))

# Banco de dados: Turso em produção (se as variáveis estiverem definidas), SQLite local caso contrário.
TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '').strip()
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN', '').strip()

if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
    # Turso te dá a URL como "libsql://nome-do-banco-org.turso.io" — o dialeto do SQLAlchemy
    # espera só o host, sem o prefixo "libsql://".
    turso_host = TURSO_DATABASE_URL.replace('libsql://', '').replace('https://', '')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite+libsql://{turso_host}?secure=true"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'auth_token': TURSO_AUTH_TOKEN}}
    print("🌐 Banco de dados: Turso (produção)")
elif IS_VERCEL:
    # Rede de segurança: se alguém publicar na Vercel sem configurar TURSO_DATABASE_URL/
    # TURSO_AUTH_TOKEN por engano, NÃO tenta gravar num arquivo local (o disco lá é
    # somente-leitura fora de /tmp, isso quebraria a aplicação inteira). Usa /tmp como
    # último recurso — funciona, mas os dados somem a qualquer momento (ambiente efêmero).
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/energisa.db'
    print("⚠️ ATENÇÃO: rodando na Vercel SEM Turso configurado — usando /tmp (dados temporários, "
          "somem a qualquer momento). Configure TURSO_DATABASE_URL e TURSO_AUTH_TOKEN.")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energisa.db'
    print("💻 Banco de dados: SQLite local (desenvolvimento)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

if not IS_VERCEL:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('templates', exist_ok=True)

app.jinja_env.globals['LOGO_B64'] = LOGO_BASE64

db = SQLAlchemy(app)

# ============================================================
# MODELOS
# ============================================================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=True)
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    must_change_password = db.Column(db.Boolean, default=True, nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' ou 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=True)
    link = db.Column(db.String(300), nullable=True)          # Link da Inscrição
    site = db.Column(db.String(300), nullable=True)          # Link do Evento
    event_type = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)      # Estado/Cidade
    country = db.Column(db.String(100), nullable=True)
    source = db.Column(db.String(20), default='manual')      # 'auto' (IA) ou 'manual' (cadastrado à mão)
    source_url = db.Column(db.String(500), nullable=True)    # URL onde a IA encontrou a informação
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    normalized_key = db.Column(db.String(300), unique=True, nullable=True)  # nome normalizado + data — trava duplicata no banco

    def days_until(self):
        if self.date:
            delta = self.date - datetime.now().date()
            return delta.days
        return None

    talks = db.relationship('Talk', backref='event', cascade='all, delete-orphan')


class Talk(db.Model):
    __tablename__ = 'talks'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    speaker = db.Column(db.String(100), nullable=True)
    time = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    normalized_key = db.Column(db.String(300), unique=True, nullable=True)  # evento + nome normalizado — trava duplicata no banco

    registrations = db.relationship('TalkRegistration', backref='talk', cascade='all, delete-orphan')


class TalkRegistration(db.Model):
    __tablename__ = 'talk_registrations'
    id = db.Column(db.Integer, primary_key=True)
    talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    evidence_path = db.Column(db.String(300), nullable=True)
    evidence_uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id])


class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    file_path = db.Column(db.String(300), nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='confirmada')
    hotel_name = db.Column(db.String(200), nullable=True)

    user = db.relationship('User', backref='registrations')
    event = db.relationship('Event', backref='registrations')


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user and user.must_change_password and f.__name__ not in ('change_password', 'logout'):
            flash('Você precisa trocar sua senha antes de continuar.', 'warning')
            return redirect(url_for('change_password'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Usa em conjunto com @login_required (colocar depois dele na pilha de decorators).
    Bloqueia o acesso de usuários comuns a rotas de administração."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(session.get('user_id'))
        if not user or not user.is_admin():
            flash('❌ Acesso restrito a administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx', 'txt', 'xlsx', 'png', 'zip', 'jpeg', 'jpg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# ARMAZENAMENTO DE ARQUIVOS (evidências) — disco local em dev, Vercel Blob em produção
# ============================================================
def salvar_arquivo(file_storage, nome_unico):
    """
    Salva um arquivo enviado pelo usuário. Retorna uma "referência" que deve ser
    guardada no banco: no ambiente local é só o nome do arquivo; no Vercel é a
    URL completa do Vercel Blob (que já é público — ver aviso na documentação).
    """
    if IS_VERCEL:
        import vercel_blob
        conteudo = file_storage.read()
        resultado = vercel_blob.put(nome_unico, conteudo)
        return resultado['url']
    else:
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_unico)
        file_storage.save(caminho)
        return nome_unico


def remover_arquivo(referencia):
    """Remove um arquivo de evidência, local ou do Vercel Blob, dado o valor salvo no banco."""
    if not referencia:
        return
    try:
        if referencia.startswith('http://') or referencia.startswith('https://'):
            import vercel_blob
            vercel_blob.delete(referencia)
        else:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], referencia))
    except Exception as e:
        print(f"⚠️ Falha ao remover arquivo '{referencia}': {e}")


def url_arquivo(referencia):
    """Retorna a URL pra abrir/baixar o arquivo, seja ele local ou do Vercel Blob."""
    if not referencia:
        return ''
    if referencia.startswith('http://') or referencia.startswith('https://'):
        return referencia
    return url_for('uploaded_file', filename=referencia)


app.jinja_env.globals['url_arquivo'] = url_arquivo


# ============================================================
# BUSCA REAL DE EVENTOS — scraping de brasilenergia.com.br/eventos
# ============================================================
import re
import unicodedata
import time
import requests as http_requests
from bs4 import BeautifulSoup

BASE_URL = "https://brasilenergia.com.br"
LISTING_URL = f"{BASE_URL}/eventos"
MAX_PAGES = int(os.environ.get('EVENTOS_MAX_PAGINAS', '15'))  # ~300 eventos, cobre bem mais de 1 ano
REQUEST_DELAY = float(os.environ.get('EVENTOS_DELAY_SEGUNDOS', '0.4'))  # educado com o servidor deles

HEADERS = {
    "User-Agent": "EnergisaEventosBot/1.0 (uso interno, agenda de eventos do setor eletrico)"
}

# Palavras-chave que indicam evento de petróleo/gás puro (a listagem mistura os dois editoriais
# e o filtro por URL não funciona — então filtramos por título como aproximação)
BLACKLIST_PETROLEO_GAS = [
    'oil', 'gas', 'gás', 'petrol', 'petróleo', 'refin', 'lng', 'upstream',
    'downstream', 'petrochemical', 'petroquímic', 'combustív', 'etanol',
    'biofuel', 'biocombust',
]


def _normalize_title(title):
    """Normaliza título para deduplicação (minúsculas, sem acento, sem espaços extras)."""
    if not title:
        return ''
    nfkd = unicodedata.normalize('NFKD', title)
    ascii_str = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'\s+', ' ', ascii_str.lower().strip())


def _event_key(title, date):
    """Chave única de evento: nome normalizado + data. Trava duplicata no nível do banco."""
    return f"{_normalize_title(title)}|{date.isoformat()}"


def _talk_key(event_id, title):
    """Chave única de palestra: evento + nome normalizado. Trava duplicata no nível do banco."""
    return f"{event_id}|{_normalize_title(title)}"


def _is_relevante(titulo):
    """Filtro best-effort: exclui eventos claramente só de petróleo/gás pelo título."""
    t = _normalize_title(titulo)
    return not any(kw in t for kw in BLACKLIST_PETROLEO_GAS)


def _listar_eventos_ids():
    """
    Varre as páginas de listagem (?pg=0,1,2...) e retorna um dict
    {event_id: (data_inicio, texto_bruto)}, onde texto_bruto é o texto completo
    do link na listagem (contém data + título + cidade/país, ex: "25/08/2026 a
    27/08/2026 Intersolar South America São Paulo, Brasil"). Usamos esse texto
    depois para extrair cidade e país, já que a página de detalhe não os traz
    separados. Para de paginar quando uma página não traz nenhum link novo.
    """
    encontrados = {}
    for pg in range(1, MAX_PAGES + 1):
        url = f"{LISTING_URL}?pg={pg}"
        resp = http_requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        links = soup.select('a[href^="/eventos/"]')
        novos_na_pagina = 0
        for a in links:
            href = a.get('href', '')
            m_id = re.match(r'^/eventos/(\d+)$', href)
            if not m_id:
                continue
            event_id = m_id.group(1)
            texto = a.get_text(strip=True)
            m_data = re.match(r'^(\d{2})/(\d{2})/(\d{4})', texto)
            if not m_data:
                continue
            dia, mes, ano = m_data.groups()
            try:
                data_inicio = datetime(int(ano), int(mes), int(dia)).date()
            except ValueError:
                continue
            if event_id not in encontrados:
                encontrados[event_id] = (data_inicio, texto)
                novos_na_pagina += 1

        if novos_na_pagina == 0:
            break
        time.sleep(REQUEST_DELAY)

    return encontrados


def _detalhar_evento(event_id):
    """Busca a página de detalhe de um evento e extrai título, local, site oficial."""
    url = f"{BASE_URL}/eventos/{event_id}"
    resp = http_requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    linhas = [l.strip() for l in soup.get_text('\n').split('\n') if l.strip()]

    titulo = None
    for i, linha in enumerate(linhas):
        if linha.startswith('Agenda /') or linha.startswith('Agenda/'):
            titulo = linha.split('/', 1)[1].strip()
            break
    if not titulo:
        return None

    def _valor_apos_label(label):
        for i, linha in enumerate(linhas):
            if linha.strip().rstrip(':').lower() == label.lower():
                for j in range(i + 1, min(i + 4, len(linhas))):
                    if linhas[j].strip():
                        return linhas[j].strip()
        return ''

    local = _valor_apos_label('Local')
    website_raw = _valor_apos_label('Website')
    organizador = _valor_apos_label('Organizador')

    m_url = re.search(r'https?://\S+', website_raw)
    site = m_url.group(0).rstrip('>').strip() if m_url else ''

    return {
        'title': titulo,
        'venue': local,  # nome do espaço/local físico (ex: "Expo Center Norte"), não é cidade/estado
        'site': site,
        'organizador': organizador,
    }


# Mapa cidade -> UF (heurística: cobre capitais e cidades mais comuns em eventos do setor de energia.
# Não é exaustivo — cidade não mapeada simplesmente não aparece no filtro por estado).
CIDADE_PARA_UF = {
    'sao paulo': 'SP', 'campinas': 'SP', 'santos': 'SP', 'guarulhos': 'SP', 'ribeirao preto': 'SP',
    'rio de janeiro': 'RJ', 'niteroi': 'RJ',
    'brasilia': 'DF',
    'belo horizonte': 'MG', 'uberlandia': 'MG',
    'salvador': 'BA',
    'fortaleza': 'CE',
    'recife': 'PE',
    'porto alegre': 'RS', 'caxias do sul': 'RS',
    'curitiba': 'PR', 'foz do iguacu': 'PR', 'londrina': 'PR',
    'manaus': 'AM',
    'belem': 'PA',
    'goiania': 'GO',
    'florianopolis': 'SC', 'joinville': 'SC', 'blumenau': 'SC',
    'vitoria': 'ES', 'vila velha': 'ES',
    'natal': 'RN',
    'joao pessoa': 'PB',
    'maceio': 'AL',
    'aracaju': 'SE',
    'teresina': 'PI',
    'sao luis': 'MA',
    'cuiaba': 'MT',
    'campo grande': 'MS',
    'palmas': 'TO',
    'porto velho': 'RO',
    'rio branco': 'AC',
    'boa vista': 'RR',
    'macapa': 'AP',
}


def _uf_por_cidade(location):
    """Tenta identificar a UF a partir do nome da cidade (campo location). Retorna None se não reconhecer."""
    if not location:
        return None
    chave = _normalize_title(location)
    return CIDADE_PARA_UF.get(chave)


app.jinja_env.globals['uf_por_cidade'] = _uf_por_cidade


def _extrair_cidade_pais(texto_bruto, titulo):
    """
    A listagem traz tudo junto no texto do link: "DD/MM/AAAA a DD/MM/AAAA Título Cidade, País".
    Removendo o intervalo de datas e o título (já conhecido pela página de detalhe),
    sobra "Cidade, País" — separamos pela última vírgula.
    """
    sem_data = re.sub(r'^\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4}\s*', '', texto_bruto).strip()

    resto = sem_data
    if titulo and sem_data.startswith(titulo):
        resto = sem_data[len(titulo):].strip()
    else:
        # Fallback: título pode ter pequenas diferenças de espaçamento/acentuação
        titulo_norm = _normalize_title(titulo)
        sem_data_norm = _normalize_title(sem_data)
        if titulo_norm and sem_data_norm.startswith(titulo_norm):
            resto = sem_data[len(titulo):].strip()

    if ',' in resto:
        cidade, pais = resto.rsplit(',', 1)
        return cidade.strip(), pais.strip()
    return resto.strip(), ''


def fetch_events_from_web():
    """
    Faz scraping de brasilenergia.com.br/eventos (agenda pública, renderizada
    no servidor, sem necessidade de JS/login). Retorna lista de dicts prontos
    para gravar no banco, ou levanta exceção em caso de falha total.
    """
    ids_com_data = _listar_eventos_ids()
    if not ids_com_data:
        raise RuntimeError("Nenhum evento encontrado na listagem — o layout do site pode ter mudado.")

    validos = []
    hoje = datetime.now().date()
    for event_id, (data_inicio, texto_bruto) in ids_com_data.items():
        if data_inicio < hoje:
            continue  # evento já passou
        try:
            detalhe = _detalhar_evento(event_id)
        except Exception as e:
            print(f"⚠️ Falha ao detalhar evento {event_id}: {e}")
            continue
        time.sleep(REQUEST_DELAY)

        if not detalhe or not detalhe['title']:
            continue
        if not _is_relevante(detalhe['title']):
            continue

        cidade, pais = _extrair_cidade_pais(texto_bruto, detalhe['title'])

        descricao_partes = []
        if detalhe['venue']:
            descricao_partes.append(f"Local: {detalhe['venue']}")
        if detalhe['organizador']:
            descricao_partes.append(f"Organização: {detalhe['organizador']}")

        validos.append({
            'title': detalhe['title'],
            'description': ' | '.join(descricao_partes),
            'date': data_inicio,
            'time': None,
            'site': detalhe['site'] or f"{BASE_URL}/eventos/{event_id}",
            'link': detalhe['site'] or f"{BASE_URL}/eventos/{event_id}",
            'event_type': '',
            'location': cidade or detalhe['venue'],
            'country': pais,
        })

    return validos


# ============================================================
# ATUALIZAÇÃO DOS EVENTOS (busca real, preserva eventos manuais)
# ============================================================
def _deduplicar_eventos_auto():
    """
    Mescla eventos automáticos duplicados (mesmo título normalizado + data) que
    ficaram no banco — de execuções antigas do scraper, antes da correção da
    paginação e da chave única. Mantém o mais antigo, move palestras/inscrições
    dele pros outros antes de apagar os duplicados, pra não perder nada.
    Também preenche a normalized_key de quem ainda não tem (backfill).
    """
    todos = Event.query.filter_by(source='auto').order_by(Event.id.asc()).all()
    grupos = {}
    for e in todos:
        chave = _event_key(e.title, e.date)
        grupos.setdefault(chave, []).append(e)

    removidos = 0
    for chave, eventos_grupo in grupos.items():
        principal = eventos_grupo[0]  # o de menor id (mais antigo)
        principal.normalized_key = chave
        for dup in eventos_grupo[1:]:
            # Move palestras do duplicado pro evento principal, em vez de apagar
            for t in Talk.query.filter_by(event_id=dup.id).all():
                t.event_id = principal.id
            # Move inscrições de evento (com hotel) também
            for r in Registration.query.filter_by(event_id=dup.id).all():
                ja_existe = Registration.query.filter_by(event_id=principal.id, user_id=r.user_id).first()
                if ja_existe:
                    db.session.delete(r)  # já tem essa pessoa no principal, evita duplicar
                else:
                    r.event_id = principal.id
            db.session.delete(dup)
            removidos += 1

    db.session.commit()
    if removidos:
        print(f"🧹 {removidos} evento(s) duplicado(s) mesclado(s) no evento principal.")
    _deduplicar_talks()
    return removidos


def _deduplicar_talks():
    """
    Mescla palestras duplicadas (mesmo evento + título normalizado), movendo as
    inscrições da duplicada pra sobrevivente antes de apagar. Também preenche a
    normalized_key de quem ainda não tem.
    """
    todas = Talk.query.order_by(Talk.id.asc()).all()
    grupos = {}
    for t in todas:
        chave = _talk_key(t.event_id, t.title)
        grupos.setdefault(chave, []).append(t)

    removidas = 0
    for chave, talks_grupo in grupos.items():
        principal = talks_grupo[0]
        principal.normalized_key = chave
        for dup in talks_grupo[1:]:
            for reg in TalkRegistration.query.filter_by(talk_id=dup.id).all():
                ja_existe = TalkRegistration.query.filter_by(talk_id=principal.id, user_id=reg.user_id).first()
                if ja_existe:
                    if reg.evidence_path:
                        remover_arquivo(reg.evidence_path)
                    db.session.delete(reg)
                else:
                    reg.talk_id = principal.id
            db.session.delete(dup)
            removidas += 1

    db.session.commit()
    if removidas:
        print(f"🧹 {removidas} palestra(s) duplicada(s) mesclada(s) na palestra principal.")
    return removidas


def update_events():
    """
    Busca eventos reais via scraping e sincroniza com o banco.
    Só cria/atualiza/remove eventos com source='auto'. Eventos cadastrados
    manualmente (source='manual') nunca são tocados por essa função.
    Se a busca falhar, os dados existentes são preservados (nada é apagado).
    """
    with app.app_context():
        _deduplicar_eventos_auto()

    print(f"🔄 Buscando eventos reais em {datetime.now()}")
    try:
        eventos = fetch_events_from_web()
    except Exception as e:
        print(f"❌ Falha ao buscar eventos: {e}")
        print("↩️ Nenhuma alteração feita — eventos existentes preservados.")
        return {'ok': False, 'error': str(e)}

    with app.app_context():
        vistos_agora = set()

        for ev_data in eventos:
            chave = _event_key(ev_data['title'], ev_data['date'])
            vistos_agora.add(chave)

            event = Event.query.filter_by(normalized_key=chave).first()

            if event and event.source == 'manual':
                # Já existe um evento cadastrado manualmente com esse nome+data —
                # a chave é única na tabela inteira, então não criamos outro nem sobrescrevemos o manual.
                continue

            if not event:
                event = Event(title=ev_data['title'], date=ev_data['date'], source='auto', normalized_key=chave)
                db.session.add(event)

            event.title = ev_data['title']
            event.description = ev_data['description']
            event.date = ev_data['date']
            event.time = ev_data['time']
            event.link = ev_data['link']
            event.site = ev_data['site']
            event.source_url = ev_data['site']
            event.event_type = ev_data['event_type']
            event.location = ev_data['location']
            event.country = ev_data['country']
            event.source = 'auto'
            event.normalized_key = chave

        # Remove eventos automáticos que sumiram da busca — mas SÓ se ainda não aconteceram.
        # Eventos com data no passado NUNCA são removidos aqui: viram histórico permanente,
        # preservando inscrições em palestras e evidências de quem participou.
        # (A busca em si já só retorna eventos futuros, então um evento passado nunca vai
        # aparecer em `vistos_agora` de qualquer forma — por isso o filtro de data é essencial,
        # senão TODO evento passado seria considerado "sumiu" e apagado.)
        hoje = datetime.now().date()
        antigos = Event.query.filter_by(source='auto').filter(Event.date >= hoje).all()
        removidos = 0
        for e in antigos:
            if (e.normalized_key or _event_key(e.title, e.date)) not in vistos_agora:
                talks = Talk.query.filter_by(event_id=e.id).all()
                for t in talks:
                    for reg in TalkRegistration.query.filter_by(talk_id=t.id).all():
                        if reg.evidence_path:
                            remover_arquivo(reg.evidence_path)
                        db.session.delete(reg)
                    db.session.delete(t)
                Registration.query.filter_by(event_id=e.id).delete()
                db.session.delete(e)
                removidos += 1

        db.session.commit()
        msg = f"✅ {len(eventos)} eventos confirmados via busca, {removidos} removidos por não aparecerem mais (apenas eventos futuros cancelados; histórico de eventos passados é preservado)."
        print(msg)
        return {'ok': True, 'count': len(eventos), 'removed': removidos}


def refresh_events():
    """Wrapper para o agendador local (APScheduler)."""
    update_events()


@app.route('/api/cron/update-events')
def cron_update_events():
    """
    Endpoint chamado pelo Vercel Cron em produção (configurado em vercel.json),
    no lugar do APScheduler local (que não funciona em ambiente serverless).
    A Vercel define automaticamente a variável de ambiente CRON_SECRET e envia
    ela como 'Authorization: Bearer <CRON_SECRET>' nas chamadas de cron —
    isso impede que qualquer pessoa de fora dispare a atualização manualmente.
    """
    cron_secret = os.environ.get('CRON_SECRET', '')
    auth_header = request.headers.get('Authorization', '')
    if not cron_secret or auth_header != f"Bearer {cron_secret}":
        return {'error': 'unauthorized'}, 401

    resultado = update_events()
    return resultado


# ============================================================
# ROTAS - AUTENTICAÇÃO
# ============================================================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role
            if user.must_change_password:
                flash('Este é seu primeiro acesso (ou sua senha foi redefinida). Cadastre uma nova senha para continuar.', 'info')
                return redirect(url_for('change_password'))
            flash(f'Bem-vindo(a), {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        senha_atual = request.form.get('current_password', '')
        nova_senha = request.form.get('new_password', '')
        confirmar = request.form.get('confirm_password', '')

        if not user.check_password(senha_atual):
            flash('Senha atual incorreta.', 'danger')
        elif len(nova_senha) < 6:
            flash('A nova senha precisa ter pelo menos 6 caracteres.', 'danger')
        elif nova_senha != confirmar:
            flash('A confirmação não bate com a nova senha.', 'danger')
        elif nova_senha == senha_atual:
            flash('A nova senha precisa ser diferente da atual.', 'danger')
        else:
            user.set_password(nova_senha)
            user.must_change_password = False
            db.session.commit()
            flash('✅ Senha alterada com sucesso!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('change_password.html', forced=user.must_change_password)


# ============================================================
# FERIADOS NACIONAIS (fixos + móveis, calculados via Páscoa)
# ============================================================
def _calcular_pascoa(ano):
    """Algoritmo de Meeus/Jones/Butcher (calendário gregoriano) pra achar o Domingo de Páscoa."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(ano, mes, dia).date()


def feriados_nacionais(ano):
    """Retorna {date: nome_do_feriado} com os feriados nacionais oficiais do Brasil,
    mais Carnaval e Corpo de Cristo (pontos facultativos, mas amplamente observados)."""
    pascoa = _calcular_pascoa(ano)
    feriados = {
        datetime(ano, 1, 1).date(): 'Confraternização Universal',
        datetime(ano, 4, 21).date(): 'Tiradentes',
        datetime(ano, 5, 1).date(): 'Dia do Trabalho',
        datetime(ano, 9, 7).date(): 'Independência do Brasil',
        datetime(ano, 10, 12).date(): 'Nossa Senhora Aparecida',
        datetime(ano, 11, 2).date(): 'Finados',
        datetime(ano, 11, 15).date(): 'Proclamação da República',
        datetime(ano, 11, 20).date(): 'Consciência Negra',
        datetime(ano, 12, 25).date(): 'Natal',
        pascoa - timedelta(days=2): 'Sexta-feira Santa',
        pascoa + timedelta(days=60): 'Corpus Christi (facultativo)',
        pascoa - timedelta(days=48): 'Carnaval (facultativo)',
        pascoa - timedelta(days=47): 'Carnaval (facultativo)',
    }
    return feriados


# ============================================================
# ROTAS - DASHBOARD
# ============================================================
def build_calendar_data(events, year, month):
    today = datetime.now().date()
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

    start_weekday = (first_day.weekday() + 1) % 7
    days_in_month = last_day.day

    event_days = {}
    for ev in events:
        if ev.date.year == year and ev.date.month == month:
            day = ev.date.day
            event_days.setdefault(day, []).append(ev)

    feriados_ano = feriados_nacionais(year)

    calendar = []
    week = []
    for _ in range(start_weekday):
        week.append(None)

    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day).date()
        is_today = (date_obj == today)
        has_event = day in event_days
        dia_eventos = event_days.get(day, [])

        week.append({
            'day': day,
            'date': date_obj,
            'is_today': is_today,
            'has_event': has_event,
            'events': dia_eventos,
            'holiday_name': feriados_ano.get(date_obj)
        })
        if len(week) == 7:
            calendar.append(week)
            week = []

    if week:
        while len(week) < 7:
            week.append(None)
        calendar.append(week)

    month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    return {
        'year': year,
        'month': month,
        'month_name': month_names[month - 1],
        'weeks': calendar,
        'today': today
    }


@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    current_user = User.query.get(session['user_id'])

    # Filtro da lista "Próximos Eventos" (separado das estatísticas do mês atual)
    list_year = request.args.get('list_year', 'todos')
    list_month = request.args.get('list_month', 'todos')
    list_country = request.args.get('list_country', 'todos')
    list_has_reg = request.args.get('list_has_reg', 'todos')
    list_scope = request.args.get('list_scope', 'todos')  # 'todos' | 'nacional' | 'internacional'
    list_uf = request.args.get('list_uf', 'todos')
    list_event_id = request.args.get('list_event_id', type=int)
    event_id = request.args.get('event_id', type=int)
    view_talk = request.args.get('view_talk', type=int)
    register_talk = request.args.get('register_talk', type=int)

    # Navegação do calendário (independente do filtro da tabela de Eventos)
    try:
        cal_month = int(request.args.get('cal_month', today.month))
        cal_year = int(request.args.get('cal_year', today.year))
    except ValueError:
        cal_month, cal_year = today.month, today.year
    if cal_month < 1:
        cal_month = 12
        cal_year -= 1
    elif cal_month > 12:
        cal_month = 1
        cal_year += 1

    all_events = Event.query.order_by(Event.date.asc()).all()

    # Estatísticas sempre baseadas no mês/ano REAL de hoje (não dependem do filtro da lista)
    events_in_month = [e for e in all_events if e.date.year == today.year and e.date.month == today.month]
    count_events_in_month = len(events_in_month)

    start_date = datetime(today.year, today.month, 1).date()
    if today.month == 12:
        end_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)

    regs_in_month = Registration.query.join(Event).filter(
        Event.date >= start_date,
        Event.date <= end_date
    ).count()

    total_registrations = Registration.query.count()

    next_upcoming = [e for e in all_events if e.date > today and (e.country or '').strip().lower() == 'brasil']
    next_event = next_upcoming[0] if next_upcoming else None
    days_until_next = next_event.days_until() if next_event else None

    # Lista "Próximos Eventos": sem limite, filtrável por ano/mês/país/inscrições
    filtered_events = all_events
    if list_year == 'todos' and list_month == 'todos' and list_country == 'todos' and list_has_reg == 'todos':
        filtered_events = [e for e in all_events if e.date >= today]
    else:
        if list_year != 'todos':
            filtered_events = [e for e in filtered_events if e.date.year == int(list_year)]
        if list_month != 'todos':
            filtered_events = [e for e in filtered_events if e.date.month == int(list_month)]
        if list_country != 'todos':
            filtered_events = [e for e in filtered_events if (e.country or '') == list_country]

    if list_has_reg == 'sim':
        ids_com_inscricao = {r.event_id for r in Registration.query.all()}
        filtered_events = [e for e in filtered_events if e.id in ids_com_inscricao]

    if list_scope == 'nacional':
        filtered_events = [e for e in filtered_events if (e.country or '').strip().lower() == 'brasil']
    elif list_scope == 'internacional':
        filtered_events = [e for e in filtered_events if e.country and e.country.strip().lower() != 'brasil']

    if list_uf != 'todos':
        filtered_events = [e for e in filtered_events if _uf_por_cidade(e.location) == list_uf]

    if list_event_id:
        filtered_events = [e for e in all_events if e.id == list_event_id]

    # O indicador "Eventos" acompanha o filtro aplicado (ano/mês/país) — mesmo total exibido na lista
    total_events = len(filtered_events)

    ufs_disponiveis = sorted({_uf_por_cidade(e.location) for e in all_events if _uf_por_cidade(e.location)})

    anos_disponiveis = sorted({e.date.year for e in all_events}, reverse=True)
    if today.year not in anos_disponiveis:
        anos_disponiveis = sorted(anos_disponiveis + [today.year], reverse=True)

    paises_disponiveis = sorted({e.country for e in all_events if e.country})

    if event_id:
        recent_registrations = Registration.query.filter_by(event_id=event_id).order_by(Registration.registration_date.desc()).limit(10).all()
        event_selected = Event.query.get(event_id)
        talks = Talk.query.filter_by(event_id=event_id).order_by(Talk.time.asc()).all() if event_selected else []
    else:
        recent_registrations = Registration.query.order_by(Registration.registration_date.desc()).limit(10).all()
        event_selected = None
        talks = []

    # Contagem de inscritos por palestra (só para as palestras exibidas nesse drill-down)
    talk_reg_counts = {}
    for t in talks:
        talk_reg_counts[t.id] = TalkRegistration.query.filter_by(talk_id=t.id).count()

    # Lista de inscritos, carregada só se o usuário clicou pra ver (view_talk)
    talk_registrants = []
    if view_talk:
        talk_registrants = TalkRegistration.query.filter_by(talk_id=view_talk).order_by(TalkRegistration.registration_date.asc()).all()

    all_users = User.query.order_by(User.name.asc()).all()

    calendar_data = build_calendar_data(all_events, cal_year, cal_month)

    return render_template(
        'dashboard.html',
        events=filtered_events,
        total_registrations=total_registrations,
        total_events=total_events,
        events_in_month=count_events_in_month,
        registrations_in_month=regs_in_month,
        next_event=next_event,
        days_until_next=days_until_next,
        recent_registrations=recent_registrations,
        anos_disponiveis=anos_disponiveis,
        paises_disponiveis=paises_disponiveis,
        list_year=list_year,
        list_month=list_month,
        list_country=list_country,
        calendar_data=calendar_data,
        cal_month=cal_month,
        cal_year=cal_year,
        today_month=today.month,
        today_year=today.year,
        list_has_reg=list_has_reg, list_scope=list_scope,
        list_uf=list_uf,
        ufs_disponiveis=ufs_disponiveis,
        list_event_id=list_event_id,
        mes_atual=today.month,
        ano_atual=today.year,
        selected_event_id=event_id,
        talks=talks,
        talk_reg_counts=talk_reg_counts,
        view_talk=view_talk,
        register_talk=register_talk,
        talk_registrants=talk_registrants,
        all_users=all_users,
        event_selected=event_selected,
        current_user=current_user
    )


# ============================================================
# ROTAS - CADASTRO
# ============================================================
@app.route('/employees')
@login_required
@admin_required
def employees():
    users = User.query.order_by(User.name.asc()).all()
    return render_template('employees.html', users=users)


@app.route('/employee/add', methods=['GET', 'POST'])
@login_required
@admin_required
def employee_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        role = request.form.get('role', 'user').strip()
        if role not in ('admin', 'user'):
            role = 'user'

        if not all([name, company, email, department]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('employee_form.html', user=None, action='add')

        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado.', 'danger')
            return render_template('employee_form.html', user=None, action='add')

        import random
        reg_num = f"USR{random.randint(10000,99999)}"
        while User.query.filter_by(registration_number=reg_num).first():
            reg_num = f"USR{random.randint(10000,99999)}"

        user = User(
            name=name,
            registration_number=reg_num,
            company=company,
            email=email,
            department=department,
            role=role
        )
        user.set_password('123456')
        user.must_change_password = True
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Senha padrão: 123456', 'success')
        return redirect(url_for('employees'))

    return render_template('employee_form.html', user=None, action='add')


@app.route('/employee/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def employee_edit(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form.get('name', '').strip()
        user.company = request.form.get('company', '').strip()
        user.email = request.form.get('email', '').strip()
        user.department = request.form.get('department', '').strip()
        role = request.form.get('role', 'user').strip()
        if role in ('admin', 'user'):
            user.role = role

        existing = User.query.filter(User.email == user.email, User.id != user.id).first()
        if existing:
            flash('Este e-mail já está em uso por outro cadastro.', 'danger')
            return render_template('employee_form.html', user=user, action='edit')

        db.session.commit()
        flash('Cadastro atualizado com sucesso!', 'success')
        return redirect(url_for('employees'))

    return render_template('employee_form.html', user=user, action='edit')


@app.route('/employee/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def employee_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session.get('user_id'):
        flash('Você não pode excluir seu próprio cadastro.', 'danger')
        return redirect(url_for('employees'))
    db.session.delete(user)
    db.session.commit()
    flash('Cadastro excluído com sucesso.', 'success')
    return redirect(url_for('employees'))


# ============================================================
# ROTAS - EVENTOS
# ============================================================
@app.route('/events')
@login_required
@admin_required
def events():
    event_list = Event.query.order_by(Event.date.asc()).all()
    return render_template('events.html', events=event_list)



@app.route('/event/add', methods=['GET', 'POST'])
@login_required
@admin_required
def event_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '')
        time = request.form.get('time', '').strip()
        link = request.form.get('link', '').strip()
        site = request.form.get('site', '').strip()
        event_type = request.form.get('event_type', '').strip()
        location = request.form.get('location', '').strip()
        country = request.form.get('country', '').strip()

        if not title or not date_str:
            flash('Título e Data são obrigatórios.', 'danger')
            return render_template('event_form.html', event=None, action='add')

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')
            return render_template('event_form.html', event=None, action='add')

        chave = _event_key(title, date_obj)
        if Event.query.filter_by(normalized_key=chave).first():
            flash('❌ Já existe um evento com esse nome nessa data. A informação não pode ser duplicada.', 'danger')
            return render_template('event_form.html', event=None, action='add')

        event = Event(
            title=title,
            description=description,
            date=date_obj,
            time=time,
            link=link,
            site=site,
            event_type=event_type,
            location=location,
            country=country,
            normalized_key=chave
        )
        db.session.add(event)
        db.session.commit()
        flash('Evento cadastrado com sucesso!', 'success')
        return redirect(url_for('events'))

    return render_template('event_form.html', event=None, action='add')


@app.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def event_edit(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form.get('title', '').strip()
        event.description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '')
        event.time = request.form.get('time', '').strip()
        event.link = request.form.get('link', '').strip()
        event.site = request.form.get('site', '').strip()
        event.event_type = request.form.get('event_type', '').strip()
        event.location = request.form.get('location', '').strip()
        event.country = request.form.get('country', '').strip()

        if not event.title or not date_str:
            flash('Título e Data são obrigatórios.', 'danger')
            return render_template('event_form.html', event=event, action='edit')

        try:
            nova_data = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')
            return render_template('event_form.html', event=event, action='edit')

        chave = _event_key(event.title, nova_data)
        outro = Event.query.filter(Event.normalized_key == chave, Event.id != event.id).first()
        if outro:
            flash('❌ Já existe outro evento com esse nome nessa data. A informação não pode ser duplicada.', 'danger')
            return render_template('event_form.html', event=event, action='edit')

        event.date = nova_data
        event.normalized_key = chave
        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('events'))

    return render_template('event_form.html', event=event, action='edit')


@app.route('/event/delete/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def event_delete(event_id):
    event = Event.query.get_or_404(event_id)
    Registration.query.filter_by(event_id=event_id).delete()
    talks = Talk.query.filter_by(event_id=event_id).all()
    for t in talks:
        for reg in TalkRegistration.query.filter_by(talk_id=t.id).all():
            if reg.evidence_path:
                remover_arquivo(reg.evidence_path)
            db.session.delete(reg)
        db.session.delete(t)
    db.session.delete(event)
    db.session.commit()
    flash('Evento excluído com sucesso.', 'success')
    return redirect(url_for('events'))


# ============================================================
# ROTAS - PALESTRAS DO EVENTO (cadastro manual, quando o scraper não traz)
# ============================================================
@app.route('/event/<int:event_id>/talks')
@login_required
@admin_required
def event_talks(event_id):
    event = Event.query.get_or_404(event_id)
    talks = Talk.query.filter_by(event_id=event_id).order_by(Talk.time.asc()).all()
    return render_template('event_talks.html', event=event, talks=talks)


@app.route('/event/<int:event_id>/talks/add', methods=['POST'])
@login_required
@admin_required
def event_talk_add(event_id):
    event = Event.query.get_or_404(event_id)
    title = request.form.get('title', '').strip()
    if not title:
        flash('❌ A palestra precisa de um título.', 'danger')
    else:
        chave = _talk_key(event.id, title)
        if Talk.query.filter_by(normalized_key=chave).first():
            flash('❌ Essa palestra já está cadastrada nesse evento. A informação não pode ser duplicada.', 'danger')
            return redirect(url_for('event_talks', event_id=event.id))

        talk = Talk(
            event_id=event.id,
            title=title,
            speaker=request.form.get('speaker', '').strip(),
            time=request.form.get('time', '').strip(),
            description=request.form.get('description', '').strip(),
            normalized_key=chave
        )
        db.session.add(talk)
        db.session.commit()
        flash('✅ Palestra adicionada.', 'success')
    return redirect(url_for('event_talks', event_id=event.id))


@app.route('/talks/<int:talk_id>/delete', methods=['POST'])
@login_required
@admin_required
def event_talk_delete(talk_id):
    talk = Talk.query.get_or_404(talk_id)
    event_id = talk.event_id
    for reg in TalkRegistration.query.filter_by(talk_id=talk.id).all():
        if reg.evidence_path:
            remover_arquivo(reg.evidence_path)
    db.session.delete(talk)
    db.session.commit()
    flash('🗑️ Palestra removida.', 'success')
    return redirect(url_for('event_talks', event_id=event_id))



# ============================================================
# ROTAS - INSCRIÇÕES EM PALESTRAS (com evidências)
# ============================================================
@app.route('/registrations')
@login_required
def registrations():
    current_user = User.query.get(session['user_id'])

    f_colaborador = request.args.get('f_colaborador', '').strip()
    f_palestra = request.args.get('f_palestra', '').strip()
    f_evento = request.args.get('f_evento', '').strip()
    f_dia = request.args.get('f_dia', '').strip()
    f_mes = request.args.get('f_mes', '').strip()
    f_ano = request.args.get('f_ano', '').strip()
    f_palestrante = request.args.get('f_palestrante', '').strip()

    todos_regs = TalkRegistration.query.order_by(TalkRegistration.registration_date.desc()).all()

    # Opções dos comboboxes: só os valores que realmente existem entre as inscrições atuais.
    # Ordem alfabética "de verdade" (ignora acento e maiúsculas/minúsculas no critério de ordenação).
    opcoes_colaborador = sorted({r.user.name for r in todos_regs}, key=_normalize_title)
    opcoes_palestra = sorted({r.talk.title for r in todos_regs}, key=_normalize_title)
    opcoes_evento = sorted({r.talk.event.title for r in todos_regs}, key=_normalize_title)
    opcoes_palestrante = sorted({r.talk.speaker for r in todos_regs if r.talk.speaker}, key=_normalize_title)

    # Dia/Mês/Ano em ordem decrescente (do maior pro menor)
    opcoes_dia = sorted({r.registration_date.day for r in todos_regs}, reverse=True)
    opcoes_mes = sorted({r.registration_date.month for r in todos_regs}, reverse=True)
    opcoes_ano = sorted({r.registration_date.year for r in todos_regs}, reverse=True)

    regs = todos_regs
    if f_colaborador:
        regs = [r for r in regs if r.user.name == f_colaborador]
    if f_palestra:
        regs = [r for r in regs if r.talk.title == f_palestra]
    if f_evento:
        regs = [r for r in regs if r.talk.event.title == f_evento]
    if f_dia:
        regs = [r for r in regs if r.registration_date.day == int(f_dia)]
    if f_mes:
        regs = [r for r in regs if r.registration_date.month == int(f_mes)]
    if f_ano:
        regs = [r for r in regs if r.registration_date.year == int(f_ano)]
    if f_palestrante:
        regs = [r for r in regs if r.talk.speaker == f_palestrante]

    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    return render_template(
        'registrations.html',
        registrations=regs,
        current_user=current_user,
        f_colaborador=f_colaborador,
        f_palestra=f_palestra,
        f_evento=f_evento,
        f_dia=f_dia,
        f_mes=f_mes,
        f_ano=f_ano,
        f_palestrante=f_palestrante,
        opcoes_colaborador=opcoes_colaborador,
        opcoes_palestra=opcoes_palestra,
        opcoes_evento=opcoes_evento,
        opcoes_dia=opcoes_dia,
        opcoes_mes=opcoes_mes,
        opcoes_ano=opcoes_ano,
        meses_nomes=meses_nomes,
        opcoes_palestrante=opcoes_palestrante
    )


@app.route('/registrations/<int:reg_id>/evidence/upload', methods=['POST'])
@login_required
def talk_evidence_upload(reg_id):
    reg = TalkRegistration.query.get_or_404(reg_id)
    current_user = User.query.get(session['user_id'])

    # Só o próprio colaborador (dono da inscrição) ou um administrador podem incluir evidência.
    if not (current_user.is_admin() or reg.user_id == current_user.id):
        flash('❌ Você só pode incluir evidência na sua própria inscrição.', 'danger')
        return redirect(url_for('registrations'))

    file = request.files.get('evidence_file')
    if not file or not file.filename or not allowed_file(file.filename):
        flash('❌ Arquivo inválido ou não selecionado.', 'danger')
        return redirect(url_for('registrations'))

    # Se já tinha evidência, remove a antiga antes de substituir.
    if reg.evidence_path:
        remover_arquivo(reg.evidence_path)

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    reg.evidence_path = salvar_arquivo(file, unique_name)
    reg.evidence_uploaded_by = current_user.id
    db.session.commit()
    flash('✅ Evidência incluída.', 'success')
    return redirect(url_for('registrations'))


@app.route('/registrations/<int:reg_id>/evidence/delete', methods=['POST'])
@login_required
def talk_evidence_delete(reg_id):
    reg = TalkRegistration.query.get_or_404(reg_id)
    current_user = User.query.get(session['user_id'])

    # Administrador remove qualquer evidência. Colaborador só remove a que ele mesmo enviou
    # (não necessariamente a mesma pessoa da inscrição, já que um admin pode ter enviado por ela).
    pode_excluir = current_user.is_admin() or reg.evidence_uploaded_by == current_user.id
    if not pode_excluir:
        flash('❌ Você só pode excluir evidências que você mesmo enviou.', 'danger')
        return redirect(url_for('registrations'))

    if reg.evidence_path:
        remover_arquivo(reg.evidence_path)
        reg.evidence_path = None
        reg.evidence_uploaded_by = None
        db.session.commit()
        flash('🗑️ Evidência removida.', 'success')
    return redirect(url_for('registrations'))


# ============================================================
# RELATÓRIO DE INSCRITOS POR EVENTO (com filtros e exportação)
# ============================================================
def _filtrar_inscritos_evento():
    """Aplica os filtros da querystring sobre Registration e retorna a lista + opções dos combos."""
    f_evento = request.args.get('r_evento', '').strip()
    f_nome = request.args.get('r_nome', '').strip()
    f_mes = request.args.get('r_mes', '').strip()
    f_ano = request.args.get('r_ano', '').strip()
    f_uf = request.args.get('r_uf', '').strip()
    f_pais = request.args.get('r_pais', '').strip()

    todas = Registration.query.join(Event).order_by(Event.date.desc()).all()

    opcoes_evento = sorted({r.event.title for r in todas}, key=_normalize_title)
    opcoes_nome = sorted({r.user.name for r in todas}, key=_normalize_title)
    opcoes_pais = sorted({r.event.country for r in todas if r.event.country})
    opcoes_uf = sorted({_uf_por_cidade(r.event.location) for r in todas if _uf_por_cidade(r.event.location)})

    regs = todas
    if f_evento:
        regs = [r for r in regs if r.event.title == f_evento]
    if f_nome:
        regs = [r for r in regs if r.user.name == f_nome]
    if f_mes:
        regs = [r for r in regs if r.event.date.month == int(f_mes)]
    if f_ano:
        regs = [r for r in regs if r.event.date.year == int(f_ano)]
    if f_uf:
        regs = [r for r in regs if _uf_por_cidade(r.event.location) == f_uf]
    if f_pais:
        regs = [r for r in regs if r.event.country == f_pais]

    filtros = {
        'r_evento': f_evento, 'r_nome': f_nome, 'r_mes': f_mes,
        'r_ano': f_ano, 'r_uf': f_uf, 'r_pais': f_pais
    }
    opcoes = {
        'opcoes_evento': opcoes_evento, 'opcoes_nome': opcoes_nome,
        'opcoes_pais': opcoes_pais, 'opcoes_uf': opcoes_uf
    }
    return regs, filtros, opcoes


@app.route('/relatorio/inscritos')
@login_required
def relatorio_inscritos():
    regs, filtros, opcoes = _filtrar_inscritos_evento()
    anos_disponiveis = sorted({r.event.date.year for r in Registration.query.join(Event).all()}, reverse=True)
    return render_template('relatorio_inscritos.html', registros=regs, anos_disponiveis=anos_disponiveis, **filtros, **opcoes)


@app.route('/relatorio/inscritos/xlsx')
@login_required
def relatorio_inscritos_xlsx():
    from openpyxl import Workbook
    from openpyxl.styles import Font
    import io

    regs, _, _ = _filtrar_inscritos_evento()

    wb = Workbook()
    ws = wb.active
    ws.title = "Inscritos"
    cabecalho = ['Colaborador', 'Departamento', 'Evento', 'Data do Evento', 'Local', 'Estado', 'País', 'Hotel', 'Data da Inscrição']
    ws.append(cabecalho)
    for cel in ws[1]:
        cel.font = Font(bold=True)

    for r in regs:
        uf = _uf_por_cidade(r.event.location) or ''
        ws.append([
            r.user.name,
            r.user.department or '',
            r.event.title,
            r.event.date.strftime('%d/%m/%Y'),
            r.event.location or '',
            uf,
            r.event.country or '',
            r.hotel_name or '',
            r.registration_date.strftime('%d/%m/%Y %H:%M') if r.registration_date else ''
        ])

    for col in ws.columns:
        largura = max(len(str(c.value)) if c.value else 0 for c in col) + 2
        ws.column_dimensions[col[0].column_letter].width = min(largura, 40)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"inscritos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/relatorio/inscritos/pdf')
@login_required
def relatorio_inscritos_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    import io

    regs, _, _ = _filtrar_inscritos_evento()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.2*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()

    elementos = [Paragraph("Relatório de Inscritos em Eventos — Energisa", styles['Title'])]

    dados = [['Colaborador', 'Depto', 'Evento', 'Data', 'Local', 'UF', 'País', 'Hotel']]
    for r in regs:
        uf = _uf_por_cidade(r.event.location) or ''
        dados.append([
            r.user.name, r.user.department or '', r.event.title,
            r.event.date.strftime('%d/%m/%Y'), r.event.location or '',
            uf, r.event.country or '', r.hotel_name or ''
        ])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0077B6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elementos.append(tabela)
    doc.build(elementos)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"inscritos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mimetype='application/pdf'
    )


@app.route('/registration/add', methods=['GET', 'POST'])
@login_required
def registration_add():
    users = User.query.order_by(User.name.asc()).all()
    events = Event.query.order_by(Event.date.asc()).all()

    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        event_id = request.form.get('event_id', '').strip()

        if not user_id or not event_id:
            flash('Selecione um colaborador e uma palestra.', 'danger')
            return render_template('registration_form.html', users=users, events=events)

        existing = Registration.query.filter_by(user_id=user_id, event_id=event_id).first()
        if existing:
            flash('Este colaborador já está inscrito nesta palestra.', 'warning')
            return render_template('registration_form.html', users=users, events=events)

        file_path = None
        if 'evidence_file' in request.files:
            file = request.files['evidence_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                file_path = salvar_arquivo(file, unique_name)

        registration = Registration(
            user_id=int(user_id),
            event_id=int(event_id),
            file_path=file_path
        )
        db.session.add(registration)
        db.session.commit()
        flash('Inscrição realizada com sucesso!', 'success')
        return redirect(url_for('registrations'))

    return render_template('registration_form.html', users=users, events=events)


@app.route('/registration/delete/<int:reg_id>', methods=['POST'])
@login_required
def registration_delete(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    current_user = User.query.get(session['user_id'])

    if not (current_user.is_admin() or reg.user_id == current_user.id):
        flash('❌ Você só pode cancelar a sua própria inscrição.', 'danger')
        return redirect(url_for('dashboard', event_id=reg.event_id))

    if reg.file_path:
        remover_arquivo(reg.file_path)
    event_id = reg.event_id
    db.session.delete(reg)
    db.session.commit()
    flash('✅ Inscrição no evento cancelada.', 'success')
    return redirect(url_for('dashboard', event_id=event_id))


@app.route('/event/<int:event_id>/inscrever', methods=['GET', 'POST'])
@login_required
def event_register_self(event_id):
    event = Event.query.get_or_404(event_id)
    current_user = User.query.get(session['user_id'])

    if request.method == 'POST':
        existing = Registration.query.filter_by(user_id=current_user.id, event_id=event.id).first()
        if existing:
            flash('⚠️ Você já está inscrito(a) neste evento.', 'danger')
            return redirect(url_for('dashboard', event_id=event.id))

        registration = Registration(
            user_id=current_user.id,
            event_id=event.id,
            hotel_name=request.form.get('hotel_name', '').strip()
        )
        db.session.add(registration)
        db.session.commit()
        flash(f'✅ Inscrição no evento "{event.title}" realizada com sucesso!', 'success')
        return redirect(url_for('dashboard', event_id=event.id))

    return render_template('event_register_self.html', event=event, current_user=current_user)


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================
# ROTA PARA ATUALIZAÇÃO MANUAL
# ============================================================
@app.route('/update-events', methods=['POST'])
@login_required
@admin_required
def manual_update():
    resultado = update_events()
    if resultado['ok']:
        flash(f"✅ Busca concluída: {resultado['count']} eventos confirmados via web search, "
              f"{resultado['removed']} removidos por não aparecerem mais na busca.", 'success')
    else:
        flash(f"❌ Falha ao buscar eventos: {resultado['error']}", 'danger')
    return redirect(request.referrer or url_for('events'))


# ============================================================
# ROTAS - INSCRIÇÃO DE COLABORADOR EM PALESTRA
# ============================================================
@app.route('/talks/<int:talk_id>/register', methods=['POST'])
@login_required
def register_talk(talk_id):
    talk = Talk.query.get_or_404(talk_id)
    user = User.query.get(session.get('user_id'))

    ja_inscrito = TalkRegistration.query.filter_by(talk_id=talk.id, user_id=user.id).first()
    if ja_inscrito:
        flash('⚠️ Você já está inscrito(a) nessa palestra.', 'danger')
    else:
        db.session.add(TalkRegistration(talk_id=talk.id, user_id=user.id))
        db.session.commit()
        flash(f'✅ Você foi inscrito(a) na palestra "{talk.title}".', 'success')

    return redirect(url_for(
        'dashboard',
        list_year=request.form.get('list_year', 'todos'),
        list_month=request.form.get('list_month', 'todos'),
        list_country=request.form.get('list_country', 'todos'),
        list_has_reg=request.form.get('list_has_reg', 'todos'),
        event_id=talk.event_id,
        view_talk=talk.id
    ))


@app.route('/talks/registration/<int:reg_id>/delete', methods=['POST'])
@login_required
def unregister_talk(reg_id):
    reg = TalkRegistration.query.get_or_404(reg_id)
    talk_id = reg.talk_id
    event_id = reg.talk.event_id
    quem_pediu = User.query.get(session.get('user_id'))

    # Administrador pode remover qualquer inscrição; usuário comum só a própria.
    pode_remover = quem_pediu and (quem_pediu.is_admin() or reg.user_id == quem_pediu.id)

    if not pode_remover:
        flash('❌ Você só pode remover a sua própria inscrição.', 'danger')
        return redirect(url_for(
            'dashboard',
            list_year=request.form.get('list_year', 'todos'),
            list_month=request.form.get('list_month', 'todos'),
            list_country=request.form.get('list_country', 'todos'),
            list_has_reg=request.form.get('list_has_reg', 'todos'),
            event_id=event_id,
            view_talk=talk_id
        ))

    nome_removido = reg.user.name
    db.session.delete(reg)
    db.session.commit()
    if quem_pediu.is_admin() and reg.user_id != quem_pediu.id:
        flash(f'✅ {nome_removido} foi removido(a) da palestra.', 'success')
    else:
        flash('✅ Sua inscrição foi removida.', 'success')
    return redirect(url_for(
        'dashboard',
        list_year=request.form.get('list_year', 'todos'),
        list_month=request.form.get('list_month', 'todos'),
        list_country=request.form.get('list_country', 'todos'),
        list_has_reg=request.form.get('list_has_reg', 'todos'),
        event_id=event_id,
        view_talk=talk_id
    ))


# ============================================================
# CRIAÇÃO DOS TEMPLATES (RESPONSIVOS COM DRILL-DOWN)
# ============================================================
def create_templates():
    templates = {
        'base.html': '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>{% block title %}Eventos Energisa{% endblock %}</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Lexend:wght@300;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --blue: #0077B6; --cyan: #00B4D8; --orange: #F77F00; --orange-light: #FDAD5C;
            --bg: #EFF4F9; --surface: #FFFFFF; --surface-2: #F5F9FC; --border: #DDE8F0;
            --text: #1A2B3C; --text-2: #5A7184; --text-3: #8FA3B1;
            --shadow: 0 4px 18px rgba(0,68,110,0.10);
            --r: 14px; --r-sm: 8px;
        }
        *, *::before, *::after { box-sizing: border-box; }
        html, body { height:100%; margin:0; padding:0; background:var(--bg); font-family:'DM Sans',sans-serif; color:var(--text); }
        a { text-decoration:none; color:var(--blue); }
        .container { max-width:1320px; margin:0 auto; padding:0 16px; }
        .site-header {
            background:var(--surface); border-bottom:1px solid var(--border);
            box-shadow:0 1px 4px rgba(0,0,0,0.06); position:sticky; top:0; z-index:100; height:auto; min-height:56px;
        }
        .site-header-inner {
            display:flex; align-items:center; justify-content:space-between;
            max-width:1320px; margin:0 auto; padding:8px 16px; gap:8px; flex-wrap:wrap;
        }
        .header-logo { display:flex; align-items:center; gap:10px; flex-shrink:0; }
        .logo-box {
            width:32px; height:32px; border-radius:8px;
            background:linear-gradient(135deg,var(--blue),var(--cyan));
            display:flex; align-items:center; justify-content:center;
            font-family:'Lexend',sans-serif; font-weight:700; font-size:12px; color:white;
        }
        .logo-info .logo-name { font-weight:600; font-size:13px; color:var(--blue); display:block; line-height:1.2; }
        .logo-info .logo-sub { font-weight:300; font-size:9px; color:var(--text-3); letter-spacing:0.8px; text-transform:uppercase; display:block; }
        .hdr-sep { display:none; }
        .pg-info .pg-title { font-family:'Lexend',sans-serif; font-weight:600; font-size:14px; display:block; }
        .pg-info .pg-sub { font-size:10px; color:var(--text-2); display:block; margin-top:1px; }
        .header-actions { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
        .today-pill {
            background:linear-gradient(135deg,var(--orange),var(--orange-light));
            color:white; font-family:'Lexend',sans-serif; font-weight:600;
            font-size:10px; padding:3px 10px; border-radius:20px;
            box-shadow:0 2px 8px rgba(247,127,0,0.28); white-space:nowrap;
        }
        .nav-links { display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
        .nav-links a { font-size:12px; font-weight:500; color:var(--text-2); padding:4px 6px; border-radius:6px; transition:all .15s; }
        .nav-links a:hover { background:var(--surface-2); color:var(--blue); }
        .card {
            background:var(--surface); border-radius:var(--r); box-shadow:var(--shadow);
            border:1px solid var(--border); overflow:hidden; margin-bottom:16px;
        }
        .card-header {
            display:flex; align-items:center; justify-content:space-between;
            padding:10px 14px; border-bottom:1px solid var(--border);
        }
        .card-header h2 { margin:0; font-family:'Lexend',sans-serif; font-size:13px; font-weight:600; color:var(--text); }
        .card-body { padding:10px 12px; }
        .form-group { display:flex; flex-direction:column; gap:4px; margin-bottom:12px; }
        .form-group label {
            font-family:'Lexend',sans-serif; font-size:9px; font-weight:600;
            color:var(--text-3); letter-spacing:0.7px; text-transform:uppercase;
        }
        .form-control {
            width:100%; padding:8px 10px; font-size:13px; color:var(--text);
            background:var(--surface-2); border:1.5px solid var(--border);
            border-radius:var(--r-sm); outline:none; transition:all .15s;
            font-family:'DM Sans',sans-serif;
        }
        .form-control:focus {
            border-color:var(--cyan); box-shadow:0 0 0 3px rgba(0,180,216,.12);
            background:var(--surface);
        }
        .form-row { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }
        .btn {
            display:inline-flex !important; align-items:center; justify-content:center;
            gap:4px; border:none; border-radius:var(--r-sm); padding:8px 14px;
            font-family:'Lexend',sans-serif; font-size:12px; font-weight:600;
            cursor:pointer; transition:all .2s; text-decoration:none;
        }
        .btn-primary { background:linear-gradient(135deg,var(--blue),var(--cyan)); color:white; box-shadow:0 3px 10px rgba(0,119,182,.28); }
        .btn-primary:hover { transform:translateY(-1px); box-shadow:0 5px 16px rgba(0,119,182,.38); }
        .btn-danger { background:#c0392b; color:white; }
        .btn-danger:hover { background:#a93226; }
        .btn-secondary { background:var(--surface-2); color:var(--text); border:1px solid var(--border); }
        .btn-secondary:hover { background:var(--border); }
        .btn-success { background:#28a745; color:white; }
        .btn-success:hover { background:#218838; }
        .btn-sm { padding:4px 8px; font-size:10px; }
        .btn-warning { background:var(--orange); color:white; }
        .btn-warning:hover { background:#D96E10; }
        .table-wrapper { overflow-x:auto; -webkit-overflow-scrolling:touch; }
        .table { width:100%; border-collapse:collapse; font-size:12px; }
        .table thead th {
            background:var(--surface-2) !important; color:var(--text-3) !important;
            padding:8px 10px; font-family:'Lexend',sans-serif; font-size:9px;
            font-weight:600; text-align:left; border-bottom:1px solid var(--border) !important;
            text-transform:uppercase; letter-spacing:0.5px; white-space:nowrap;
        }
        .table tbody tr { border-bottom:1px solid var(--border); transition:background .12s; }
        .table tbody tr:hover { background:#F4F8FB !important; }
        .table tbody td { padding:8px 10px; vertical-align:middle; }
        .alert {
            padding:10px 14px; border-radius:var(--r-sm); margin-bottom:14px; font-size:12px;
        }
        .alert-success { background:#d4edda; color:#155724; border:1px solid #c3e6cb; }
        .alert-danger  { background:#f8d7da; color:#721c24; border:1px solid #f5c6cb; }
        .alert-warning { background:#fff3cd; color:#856404; border:1px solid #ffeeba; }
        .alert-info    { background:#d1ecf1; color:#0c5460; border:1px solid #bee5eb; }
        .text-center { text-align:center; }
        .mt-20 { margin-top:20px; }
        .mb-20 { margin-bottom:20px; }
        .flex { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
        .flex-between { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; }
        .gap-8 { gap:8px; }
        .badge {
            display:inline-block; padding:2px 8px; border-radius:20px;
            font-size:10px; font-weight:600; background:var(--surface-2); color:var(--text-2);
        }
        .link-copy {
            display:flex; flex-direction:column; gap:2px;
        }
        .link-copy a {
            font-size:11px; word-break:break-all;
        }
        .link-copy .url-text {
            font-size:9px; color:var(--text-3); word-break:break-all;
        }
        .talk-item {
            background:var(--surface-2); padding:8px 12px; border-radius:var(--r-sm); margin-bottom:6px;
        }
        .talk-item strong { color:var(--blue); }
        .talk-item .talk-time { font-weight:600; color:var(--text-2); margin-right:8px; }
        @media (max-width:768px) {
            .site-header-inner { padding:6px 10px; }
            .pg-info .pg-sub { display:none; }
            .form-row { grid-template-columns:1fr; }
            .nav-links a { font-size:11px; padding:3px 5px; }
            .header-actions .today-pill { font-size:9px; padding:2px 8px; }
            .table th, .table td { padding:6px 6px; font-size:11px; }
            .card-header h2 { font-size:12px; }
            .btn { font-size:11px; padding:6px 10px; }
            .dashboard-grid { grid-template-columns:1fr !important; max-width:100% !important; }
            .card-header { flex-direction:column; align-items:stretch !important; }
            .card-header form { width:100%; }
            .card-header form select, .card-header form input { max-width:100%; flex:1 1 auto; min-width:0; }
        }
        @media (max-width:480px) {
            .container { padding:0 8px; }
            .site-header-inner { flex-direction:column; align-items:stretch; gap:4px; }
            .header-logo { justify-content:center; }
            .pg-info { text-align:center; }
            .header-actions { justify-content:center; flex-wrap:wrap; }
            .today-pill { display:none; }
            .nav-links { justify-content:center; }
            .card-body { padding:8px; }
            .table th, .table td { padding:4px 4px; font-size:10px; }
            .link-copy a { font-size:10px; }
            .link-copy .url-text { font-size:8px; word-break:break-all; display:block; max-width:100%; }
            .card-header form select, .card-header form input { font-size:11px; padding:4px 6px; }
        }
    </style>
</head>
<body>
    <header class="site-header">
        <div class="site-header-inner">
            <div class="header-logo">
                <img src="data:image/png;base64,{{ LOGO_B64 }}" alt="Eventos Energisa" style="height:32px; width:auto; display:block;">
                <div class="logo-info">
                    <span class="logo-sub">Eventos</span>
                </div>
            </div>
            <div class="hdr-sep"></div>
            <div class="pg-info">
                <span class="pg-title">{% block page_title %}Dashboard{% endblock %}</span>
                <span class="pg-sub">{% block page_sub %}Distribuição de Energia{% endblock %}</span>
            </div>
            <div class="header-actions">
                <span class="today-pill">{{ now.strftime('%d/%m/%Y') if now else '' }}</span>
                {% if session.user_id %}
                <div class="nav-links">
                    <a href="{{ url_for('dashboard') }}">Início</a>
                    {% if session.user_role == 'admin' %}
                    <a href="{{ url_for('employees') }}">Cadastro</a>
                    <a href="{{ url_for('events') }}">Eventos</a>
                    {% endif %}
                    <a href="{{ url_for('registrations') }}">Inscrições</a>
                    <a href="{{ url_for('relatorio_inscritos') }}">Relatório</a>
                    <a href="{{ url_for('logout') }}" style="color:var(--vermelho);">Sair</a>
                </div>
                {% endif %}
            </div>
        </div>
    </header>
    <main class="container" style="padding-top:16px; padding-bottom:32px;">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
</body>
</html>''',

        'login.html': '''{% extends "base.html" %}
{% block title %}Login - Eventos Energisa{% endblock %}
{% block page_title %}Acesso ao Sistema{% endblock %}
{% block page_sub %}Autenticação{% endblock %}
{% block content %}
<div style="max-width:400px; margin:30px auto;">
    <div class="card">
        <div class="card-header"><h2>Login</h2></div>
        <div class="card-body">
            <form method="post" action="{{ url_for('login') }}">
                <div class="form-group">
                    <label>E-mail</label>
                    <input type="email" name="email" class="form-control" placeholder="seu@email.com" required>
                </div>
                <div class="form-group">
                    <label>Senha</label>
                    <div style="position:relative;">
                        <input type="password" name="password" id="password" class="form-control" placeholder="Digite sua senha" required>
                        <span onclick="togglePassword()" style="position:absolute; right:12px; top:50%; transform:translateY(-50%); cursor:pointer; font-size:18px;">👁️</span>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;">Entrar</button>
            </form>
            <p style="margin-top:14px; font-size:11px; color:var(--text-3); text-align:center;">
                Primeiro acesso: senha padrão <strong>123456</strong>
            </p>
        </div>
    </div>
</div>
<script>
    function togglePassword() {
        var pwd = document.getElementById('password');
        pwd.type = (pwd.type === 'password') ? 'text' : 'password';
    }
</script>
{% endblock %}''',

        'change_password.html': '''{% extends "base.html" %}
{% block title %}Trocar Senha - Eventos Energisa{% endblock %}
{% block page_title %}Trocar Senha{% endblock %}
{% block page_sub %}Segurança da conta{% endblock %}
{% block content %}
<div style="max-width:400px; margin:30px auto;">
    <div class="card">
        <div class="card-header"><h2>{% if forced %}Primeiro acesso — defina sua senha{% else %}Trocar senha{% endif %}</h2></div>
        <div class="card-body">
            {% if forced %}
                <p style="font-size:12px; color:var(--text-3); margin-bottom:12px;">
                    Por segurança, você precisa trocar a senha padrão antes de continuar usando o sistema.
                </p>
            {% endif %}
            <form method="post" action="{{ url_for('change_password') }}">
                <div class="form-group">
                    <label>Senha atual</label>
                    <input type="password" name="current_password" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Nova senha</label>
                    <input type="password" name="new_password" class="form-control" minlength="6" required>
                </div>
                <div class="form-group">
                    <label>Confirmar nova senha</label>
                    <input type="password" name="confirm_password" class="form-control" minlength="6" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;">Salvar nova senha</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}''',


        'dashboard.html': '''{% extends "base.html" %}
{% block title %}Dashboard - Eventos Energisa{% endblock %}
{% block page_title %}Visão Geral{% endblock %}
{% block page_sub %}Eventos e Indicadores{% endblock %}
{% block content %}
<div style="max-width:760px; margin:0 auto;">
<div class="flex" style="gap:12px; margin-bottom:16px; flex-wrap:wrap;">
    {% set filtro_reg_ativo = (list_has_reg == 'sim') %}
    <a href="{% if filtro_reg_ativo %}{{ url_for('dashboard', list_year='todos', list_month='todos', list_country='todos', list_has_reg='todos') }}{% else %}{{ url_for('dashboard', list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg='sim') }}{% endif %}" class="card" style="flex:1; min-width:130px; text-decoration:none; color:inherit; display:block; {% if filtro_reg_ativo %}border-color:var(--blue); box-shadow:0 0 0 1px var(--blue);{% endif %}">
        <div class="card-body" style="padding:8px 12px;">
            <div style="font-size:9px; color:var(--text-3); text-transform:uppercase;">Total de Inscrições</div>
            <div style="font-size:20px; font-weight:700; color:var(--blue);">{{ total_registrations }}</div>
        </div>
    </a>
    <div class="card" style="flex:1; min-width:130px;">
        <div class="card-body" style="padding:8px 12px;">
            <div style="font-size:9px; color:var(--text-3); text-transform:uppercase;">Total de Eventos</div>
            <div style="font-size:20px; font-weight:700; color:var(--cyan);">{{ total_events }}</div>
        </div>
    </div>
    {% set mes_filtrado_ativo = (list_month|string == mes_atual|string and list_year|string == ano_atual|string) %}
    <a href="{% if mes_filtrado_ativo %}{{ url_for('dashboard', list_year='todos', list_month='todos', list_country='todos', list_has_reg='todos') }}{% else %}{{ url_for('dashboard', list_year=ano_atual, list_month=mes_atual, list_country='todos', list_has_reg='todos') }}{% endif %}" class="card" style="flex:1; min-width:130px; text-decoration:none; color:inherit; display:block; {% if mes_filtrado_ativo %}border-color:var(--orange); box-shadow:0 0 0 1px var(--orange);{% endif %}">
        <div class="card-body" style="padding:8px 12px;">
            <div style="font-size:9px; color:var(--text-3); text-transform:uppercase;">Eventos no Mês</div>
            <div style="font-size:20px; font-weight:700; color:var(--orange);">{{ events_in_month }}</div>
        </div>
    </a>
    <div class="card" style="flex:1; min-width:130px;">
        <div class="card-body" style="padding:8px 12px;">
            <div style="font-size:9px; color:var(--text-3); text-transform:uppercase;">Inscrições no Mês</div>
            <div style="font-size:20px; font-weight:700; color:var(--orange-light);">{{ registrations_in_month }}</div>
        </div>
    </div>
    {% if next_event %}
        {% set filtro_prox_ativo = (list_event_id == next_event.id) %}
        <a href="{% if filtro_prox_ativo %}{{ url_for('dashboard', list_year='todos', list_month='todos', list_country='todos', list_has_reg='todos') }}{% else %}{{ url_for('dashboard', list_event_id=next_event.id) }}{% endif %}" class="card" style="flex:1; min-width:140px; text-decoration:none; color:inherit; display:block; {% if filtro_prox_ativo %}border-color:var(--orange); box-shadow:0 0 0 1px var(--orange);{% endif %}">
            <div class="card-body" style="padding:8px 12px;">
                <div style="font-size:9px; color:var(--text-3); text-transform:uppercase;">Próximo evento</div>
                <div style="font-size:13px; font-weight:600;">
                    {{ next_event.title }}<br><span style="font-size:11px; color:var(--orange);">{{ days_until_next }} dias</span>
                </div>
            </div>
        </a>
    {% else %}
        <div class="card" style="flex:1; min-width:140px;">
            <div class="card-body" style="padding:8px 12px;">
                <div style="font-size:9px; color:var(--text-3); text-transform:uppercase;">Próximo evento</div>
                <div style="font-size:13px; font-weight:600;">Nenhum</div>
            </div>
        </div>
    {% endif %}
</div>
</div>

<div class="dashboard-grid" style="max-width:950px; margin:0 auto; display:grid; grid-template-columns:300px 1fr; gap:16px; align-items:start;">

<!-- Calendário -->
<div class="card">
    <div class="card-header" style="padding:8px 12px;">
        <h2 style="font-size:13px;">{{ calendar_data.month_name }} {{ calendar_data.year }}</h2>
        <div class="flex" style="gap:3px;">
            <a href="{{ url_for('dashboard', cal_month=cal_month-1, cal_year=cal_year, list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf) }}" class="btn btn-secondary btn-sm" style="padding:2px 8px; font-size:11px;">‹</a>
            <a href="{{ url_for('dashboard', cal_month=today_month, cal_year=today_year, list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf) }}" class="btn btn-secondary btn-sm" style="padding:2px 8px; font-size:10px;">Hoje</a>
            <a href="{{ url_for('dashboard', cal_month=cal_month+1, cal_year=cal_year, list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf) }}" class="btn btn-secondary btn-sm" style="padding:2px 8px; font-size:11px;">›</a>
        </div>
    </div>
    <div class="card-body" style="padding:8px;">
        <table style="width:100%; border-collapse:collapse; text-align:center;">
            <thead>
                <tr>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">D</th>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">S</th>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">T</th>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">Q</th>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">Q</th>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">S</th>
                    <th style="font-size:9px; color:var(--text-3); padding:2px;">S</th>
                </tr>
            </thead>
            <tbody>
                {% for week in calendar_data.weeks %}
                <tr>
                    {% for day in week %}
                        <td style="padding:2px;">
                            {% if day %}
                                {% set tooltip %}{% if day.holiday_name %}{{ day.holiday_name }}{% endif %}{% for ev in day.events %}{% if day.holiday_name or not loop.first %} · {% endif %}{{ ev.title }}{% endfor %}{% endset %}
                                {% if day.events or day.holiday_name %}
                                    <a href="javascript:void(0);" onclick="document.getElementById('modal-content').innerHTML = document.getElementById('cal-data-{{ day.date.strftime('%Y%m%d') }}').innerHTML; document.getElementById('event-modal').style.display='flex';"
                                       title="{{ tooltip }}"
                                       style="display:flex; align-items:center; justify-content:center; width:26px; height:26px; margin:0 auto; border-radius:50%; font-size:11px; text-decoration:none; cursor:pointer;
                                              {% if day.holiday_name %}box-shadow:0 0 0 2px #dc3545;{% endif %}
                                              {% if day.is_today %}background:var(--orange); color:white; font-weight:700;{% elif day.has_event %}background:var(--surface-2); color:var(--blue); font-weight:600;{% elif day.holiday_name %}color:#dc3545; font-weight:600;{% else %}color:var(--text-2);{% endif %}">
                                        {{ day.day }}
                                    </a>
                                {% else %}
                                    <a href="{{ url_for('dashboard', list_year=day.date.year, list_month=day.date.month, list_country='todos', list_has_reg='todos') }}"
                                       style="display:flex; align-items:center; justify-content:center; width:26px; height:26px; margin:0 auto; border-radius:50%; font-size:11px; text-decoration:none; color:var(--text-2);">
                                        {{ day.day }}
                                    </a>
                                {% endif %}
                            {% endif %}
                        </td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div style="margin-top:6px; font-size:9px; color:var(--text-3); display:flex; gap:8px; flex-wrap:wrap;">
            <span><span style="display:inline-block; width:8px; height:8px; border-radius:50%; box-shadow:0 0 0 2px #dc3545; margin-right:2px;"></span>Feriado nacional</span>
            <span><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--surface-2); margin-right:2px;"></span>Tem evento</span>
        </div>
    </div>

    <!-- Dados ocultos por dia (evento+inscritos e/ou feriado), usados pelo pop-up ao clicar no dia -->
    {% for week in calendar_data.weeks %}{% for day in week %}{% if day and (day.events or day.holiday_name) %}
        <div id="cal-data-{{ day.date.strftime('%Y%m%d') }}" style="display:none;">
            {% if day.holiday_name %}
                <div style="margin-bottom:10px; padding:6px 8px; background:#f8d7da; border-radius:4px; color:#842029; font-size:12px;">
                    🎉 Feriado: <strong>{{ day.holiday_name }}</strong>
                </div>
            {% endif %}
            {% for ev in day.events %}
                <div style="margin-bottom:10px;">
                    <strong style="color:var(--blue); font-size:13px;">{{ ev.title }}</strong>
                    <div style="font-size:11px; color:var(--text-3); margin-bottom:4px;">
                        📅 {{ ev.date.strftime('%d/%m/%Y') }}
                        {% set uf = uf_por_cidade(ev.location) %}
                        {% if ev.location %} · 📍 {{ ev.location }}{% if uf %} ({{ uf }}){% endif %}{% endif %}
                        {% if ev.country %} · {{ ev.country }}{% endif %}
                    </div>
                    <ul style="list-style:none; margin:4px 0 0 0; padding:0; font-size:12px;">
                        {% for reg in ev.registrations %}
                            <li style="display:flex; justify-content:space-between; align-items:center; padding:2px 0;">
                                <span>
                                    {{ reg.user.name }}{% if reg.hotel_name %} — 🏨 {{ reg.hotel_name }}{% endif %}
                                    {% if reg.user_id == current_user.id %}<span style="color:var(--blue); font-size:10px;">— você</span>{% endif %}
                                </span>
                                {% if current_user.is_admin() or reg.user_id == current_user.id %}
                                    <form method="post" action="{{ url_for('registration_delete', reg_id=reg.id) }}" onsubmit="return confirm('{{ 'Cancelar sua inscrição neste evento?' if reg.user_id == current_user.id else 'Remover ' + reg.user.name + ' deste evento?' }}');">
                                        <button type="submit" style="border:none; background:none; color:var(--text-3); cursor:pointer; font-size:11px;" title="Cancelar inscrição">❌</button>
                                    </form>
                                {% endif %}
                            </li>
                        {% else %}
                            <li style="color:var(--text-3);">Ninguém inscrito ainda.</li>
                        {% endfor %}
                    </ul>
                </div>
            {% endfor %}
        </div>
    {% endif %}{% endfor %}{% endfor %}
</div>

<!-- Modal de inscritos no evento (compartilhado por todos os dias do calendário e pelo ícone de cada evento) -->
<div id="event-modal" onclick="if(event.target===this) this.style.display='none';" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
    <div style="background:var(--surface); border-radius:var(--r-md); padding:16px; max-width:360px; width:90%; max-height:70vh; overflow-y:auto; position:relative;">
        <button onclick="document.getElementById('event-modal').style.display='none';" style="position:absolute; top:8px; right:8px; border:none; background:none; font-size:16px; cursor:pointer; color:var(--text-3);">✕</button>
        <h3 style="margin:0 0 10px 0; font-size:14px;">👥 Inscritos</h3>
        <div id="modal-content"></div>
    </div>
</div>

<div class="card">

    <!-- Próximos Eventos com filtro por ano/mês/país/inscrições e drill-down para palestras -->
    <div class="card-header" style="flex-wrap:wrap; gap:8px;">
        <h2 style="font-size:13px;">
            Eventos ({{ events|length }})
            {% if list_has_reg == 'sim' %}
                <span style="font-size:10px; font-weight:normal; color:var(--text-3);">— com inscrições
                    <a href="{{ url_for('dashboard', list_year=list_year, list_month=list_month, list_country=list_country) }}" style="margin-left:4px; color:var(--blue);">[remover]</a>
                </span>
            {% endif %}
        </h2>
        <form method="get" action="{{ url_for('dashboard') }}" style="display:flex; gap:4px; align-items:center; flex-wrap:wrap;">
            <input type="hidden" name="list_has_reg" value="{{ list_has_reg }}">
            <select name="list_month" style="padding:3px 6px; font-size:11px; border-radius:4px; border:1px solid var(--border); background:var(--surface);">
                <option value="todos" {% if list_month == 'todos' %}selected{% endif %}>Todos os meses</option>
                {% for m in range(1, 13) %}
                    <option value="{{ m }}" {% if list_month|string == m|string %}selected{% endif %}>{{ "%02d"|format(m) }}</option>
                {% endfor %}
            </select>
            <select name="list_year" style="padding:3px 6px; font-size:11px; border-radius:4px; border:1px solid var(--border); background:var(--surface);">
                <option value="todos" {% if list_year == 'todos' %}selected{% endif %}>Todos os anos</option>
                {% for y in anos_disponiveis %}
                    <option value="{{ y }}" {% if list_year|string == y|string %}selected{% endif %}>{{ y }}</option>
                {% endfor %}
            </select>
            <select name="list_country" id="select-list-country" style="padding:3px 6px; font-size:11px; border-radius:4px; border:1px solid var(--border); background:var(--surface); max-width:120px;">
                <option value="todos" {% if list_country == 'todos' %}selected{% endif %}>Todos os países</option>
                {% for p in paises_disponiveis %}
                    <option value="{{ p }}" data-brasil="{{ '1' if p.strip().lower() == 'brasil' else '0' }}" {% if list_country == p %}selected{% endif %}>{{ p }}</option>
                {% endfor %}
            </select>
            <select name="list_scope" id="select-list-scope" onchange="filtrarPaisesPorEscopo()" style="padding:3px 6px; font-size:11px; border-radius:4px; border:1px solid var(--border); background:var(--surface);">
                <option value="todos" {% if list_scope == 'todos' %}selected{% endif %}>Nacional + Internacional</option>
                <option value="nacional" {% if list_scope == 'nacional' %}selected{% endif %}>Só Nacionais</option>
                <option value="internacional" {% if list_scope == 'internacional' %}selected{% endif %}>Só Internacionais</option>
            </select>
            <select name="list_uf" style="padding:3px 6px; font-size:11px; border-radius:4px; border:1px solid var(--border); background:var(--surface);">
                <option value="todos" {% if list_uf == 'todos' %}selected{% endif %}>Todos os estados</option>
                {% for uf in ufs_disponiveis %}
                    <option value="{{ uf }}" {% if list_uf == uf %}selected{% endif %}>{{ uf }}</option>
                {% endfor %}
            </select>
            <button type="submit" class="btn btn-primary btn-sm" style="padding:3px 10px; font-size:11px;">Filtrar</button>
        </form>
        <script>
            function filtrarPaisesPorEscopo() {
                var escopo = document.getElementById('select-list-scope').value;
                var selectPais = document.getElementById('select-list-country');
                var opcoes = selectPais.querySelectorAll('option[data-brasil]');
                opcoes.forEach(function (opt) {
                    var isBrasil = opt.getAttribute('data-brasil') === '1';
                    if (escopo === 'nacional') {
                        opt.hidden = !isBrasil;
                    } else if (escopo === 'internacional') {
                        opt.hidden = isBrasil;
                    } else {
                        opt.hidden = false;
                    }
                });
                var selecionada = selectPais.options[selectPais.selectedIndex];
                if (selecionada && selecionada.hidden) {
                    selectPais.value = 'todos';
                }
            }
            document.addEventListener('DOMContentLoaded', filtrarPaisesPorEscopo);
        </script>
    </div>
    <div class="card-body" style="padding:6px 10px; max-height:420px; overflow-y:auto;">
        {% if events %}
            <ul style="list-style:none; padding:0; margin:0;">
            {% for ev in events %}
                <li style="padding:8px 0; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; 
                           {% if selected_event_id == ev.id %}background:var(--surface-2); border-left:3px solid var(--orange); padding-left:8px;{% endif %}">
                    <div style="flex:1; min-width:120px;">
                        <a href="{{ url_for('dashboard', list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf, event_id=ev.id) }}" style="display:block; text-decoration:none; color:var(--text);">
                            <strong style="font-size:13px;">{{ ev.title }}</strong><br>
                            <span style="font-size:11px; color:var(--text-2);">
                                {{ ev.date.strftime('%d/%m/%Y') }} {% if ev.time %} - {{ ev.time }}{% endif %}
                            </span><br>
                            {% if ev.location and ev.country %}
                                <span style="font-size:10px; color:var(--text-3);">📍 {{ ev.location }}, {{ ev.country }}</span>
                            {% elif ev.location %}
                                <span style="font-size:10px; color:var(--text-3);">📍 {{ ev.location }}</span>
                            {% elif ev.country %}
                                <span style="font-size:10px; color:var(--text-3);">📍 {{ ev.country }}</span>
                            {% endif %}
                            {% if ev.event_type %}<span class="badge" style="font-size:9px;">{{ ev.event_type }}</span>{% endif %}
                        </a>
                        <!-- Links copiáveis -->
                        <div class="link-copy" style="margin-top:4px;">
                            {% if ev.site %}
                                <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
                                    <span style="font-size:11px;">🌐</span>
                                    <a href="{{ ev.site }}" target="_blank" style="font-size:11px;">Site do Evento</a>
                                    <span class="url-text" style="font-size:9px; color:var(--text-3);">{{ ev.site }}</span>
                                </div>
                            {% endif %}
                            {% if ev.link %}
                                <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
                                    <span style="font-size:11px;">📝</span>
                                    <a href="{{ ev.link }}" target="_blank" style="font-size:11px;">Inscrição</a>
                                    <span class="url-text" style="font-size:9px; color:var(--text-3);">{{ ev.link }}</span>
                                </div>
                            {% endif %}
                            <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
                                <span style="font-size:11px;">🧳</span>
                                <a href="{{ url_for('event_register_self', event_id=ev.id) }}" style="font-size:11px;">Inscrever-me neste evento</a>
                                <a href="javascript:void(0);" onclick="document.getElementById('modal-content').innerHTML = document.getElementById('event-regs-{{ ev.id }}').innerHTML; document.getElementById('event-modal').style.display='flex';"
                                   style="font-size:11px; margin-left:4px; cursor:pointer;" title="Ver quem está inscrito">👁️ ({{ ev.registrations|length }})</a>
                            </div>
                            <div id="event-regs-{{ ev.id }}" style="display:none;">
                                <strong style="color:var(--blue); font-size:13px;">{{ ev.title }}</strong>
                                <ul style="list-style:none; margin:4px 0 0 0; padding:0; font-size:12px;">
                                    {% for reg in ev.registrations %}
                                        <li style="display:flex; justify-content:space-between; align-items:center; padding:2px 0;">
                                            <span>
                                                {{ reg.user.name }}{% if reg.hotel_name %} — 🏨 {{ reg.hotel_name }}{% endif %}
                                                {% if reg.user_id == current_user.id %}<span style="color:var(--blue); font-size:10px;">— você</span>{% endif %}
                                            </span>
                                            {% if current_user.is_admin() or reg.user_id == current_user.id %}
                                                <form method="post" action="{{ url_for('registration_delete', reg_id=reg.id) }}" onsubmit="return confirm('{{ 'Cancelar sua inscrição neste evento?' if reg.user_id == current_user.id else 'Remover ' + reg.user.name + ' deste evento?' }}');">
                                                    <button type="submit" style="border:none; background:none; color:var(--text-3); cursor:pointer; font-size:11px;" title="Cancelar inscrição">❌</button>
                                                </form>
                                            {% endif %}
                                        </li>
                                    {% else %}
                                        <li style="color:var(--text-3);">Ninguém inscrito ainda.</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                        <!-- Exibe palestras se for o evento selecionado -->
                        {% if selected_event_id == ev.id and talks %}
                            <div style="margin-top:8px; padding:8px; background:var(--surface); border-radius:var(--r-sm); border:1px solid var(--border);">
                                <strong style="font-size:12px; color:var(--blue);">📋 Palestras:</strong>
                                {% for talk in talks %}
                                    <div class="talk-item">
                                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:6px; flex-wrap:wrap;">
                                            <div>
                                                <span class="talk-time">{{ talk.time }}</span>
                                                <strong>{{ talk.title }}</strong>
                                                {% if talk.speaker %}<span style="font-size:11px; color:var(--text-2);"> - {{ talk.speaker }}</span>{% endif %}
                                                <div style="font-size:11px; color:var(--text-3);">{{ talk.description }}</div>
                                            </div>
                                            <div style="display:flex; gap:6px; align-items:center; white-space:nowrap;">
                                                <a href="{{ url_for('dashboard', list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf, event_id=ev.id, register_talk=(None if register_talk == talk.id else talk.id), view_talk=view_talk) }}"
                                                   title="Inscrever-se nessa palestra" style="font-size:14px; text-decoration:none;">➕👤</a>
                                                <a href="{{ url_for('dashboard', list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf, event_id=ev.id, view_talk=(None if view_talk == talk.id else talk.id), register_talk=register_talk) }}"
                                                   title="Ver quem já está inscrito" style="font-size:14px; text-decoration:none;">👁️ <span style="font-size:10px; color:var(--text-3);">({{ talk_reg_counts.get(talk.id, 0) }})</span></a>
                                            </div>
                                        </div>

                                        {% if register_talk == talk.id %}
                                            <form id="form-inscrever-{{ talk.id }}" method="post" action="{{ url_for('register_talk', talk_id=talk.id) }}" style="margin-top:6px; display:flex; gap:4px; align-items:center; flex-wrap:wrap; padding:8px; background:#fff3cd; border:2px solid #f77f00; border-radius:6px;">
                                                <input type="hidden" name="list_year" value="{{ list_year }}">
                                                <input type="hidden" name="list_month" value="{{ list_month }}">
                                                <input type="hidden" name="list_country" value="{{ list_country }}">
                                                <input type="hidden" name="list_has_reg" value="{{ list_has_reg }}">
                                                <span style="font-size:11px; color:#663c00; font-weight:600;">Confirmar sua inscrição nessa palestra?</span>
                                                <button type="submit" class="btn btn-primary btn-sm" style="padding:3px 10px; font-size:11px;">✅ Inscrever-me</button>
                                            </form>
                                            <script>
                                                document.getElementById('form-inscrever-{{ talk.id }}').scrollIntoView({behavior: 'smooth', block: 'center'});
                                            </script>
                                        {% endif %}

                                        {% if view_talk == talk.id %}
                                            <div style="margin-top:6px; padding:6px; background:var(--surface-2); border-radius:4px;">
                                                {% if talk_registrants %}
                                                    <strong style="font-size:11px; color:var(--text-2);">Inscritos:</strong>
                                                    <ul style="list-style:none; margin:4px 0 0 0; padding:0; font-size:11px;">
                                                        {% for reg in talk_registrants %}
                                                            <li style="display:flex; justify-content:space-between; align-items:center; padding:2px 0;">
                                                                <span>
                                                                    {{ reg.user.name }} <span style="color:var(--text-3);">({{ reg.user.department }})</span>
                                                                    {% if reg.user_id == session.get('user_id') %}<span style="color:var(--blue); font-size:10px;">— você</span>{% endif %}
                                                                </span>
                                                                {% if reg.user_id == session.get('user_id') or current_user.is_admin() %}
                                                                    <form method="post" action="{{ url_for('unregister_talk', reg_id=reg.id) }}" onsubmit="return confirm('{{ 'Remover sua inscrição dessa palestra?' if reg.user_id == session.get('user_id') else 'Remover ' + reg.user.name + ' dessa palestra?' }}');" style="display:inline;">
                                                                        <input type="hidden" name="list_year" value="{{ list_year }}">
                                                                        <input type="hidden" name="list_month" value="{{ list_month }}">
                                                                        <input type="hidden" name="list_country" value="{{ list_country }}">
                                                                        <input type="hidden" name="list_has_reg" value="{{ list_has_reg }}">
                                                                        <button type="submit" title="Remover inscrição" style="border:none; background:none; color:var(--text-3); cursor:pointer; font-size:11px;">❌</button>
                                                                    </form>
                                                                {% endif %}
                                                            </li>
                                                        {% endfor %}
                                                    </ul>
                                                {% else %}
                                                    <span style="font-size:11px; color:var(--text-3);">Ninguém inscrito ainda nessa palestra.</span>
                                                {% endif %}
                                            </div>
                                        {% endif %}
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
                        <span style="font-size:11px; color:var(--orange);">{{ ev.days_until() }} dias</span>
                        {% if selected_event_id == ev.id %}
                            <a href="{{ url_for('dashboard', list_year=list_year, list_month=list_month, list_country=list_country, list_has_reg=list_has_reg, list_scope=list_scope, list_uf=list_uf) }}" class="btn btn-secondary btn-sm" style="padding:2px 8px; font-size:10px;">Fechar</a>
                        {% endif %}
                    </div>
                </li>
            {% endfor %}
            </ul>
        {% else %}
            <p>Nenhum evento encontrado para esse filtro.</p>
        {% endif %}
    </div>
</div>
</div>
{% endblock %}''',

        'employees.html': '''{% extends "base.html" %}
{% block title %}Cadastro - Energisa{% endblock %}
{% block page_title %}Cadastro{% endblock %}
{% block page_sub %}Colaboradores{% endblock %}
{% block content %}
<div class="flex-between mb-20"><div></div><a href="{{ url_for('employee_add') }}" class="btn btn-success">+ Novo Cadastro</a></div>
<div class="card">
    <div class="card-header"><h2>Lista de Cadastros</h2></div>
    <div class="card-body">
        <div class="table-wrapper">
            <table class="table">
                <thead><tr><th>Nome</th><th>Empresa</th><th>E-mail</th><th>Diretoria/Departamento</th><th>Perfil</th><th>Ações</th></tr></thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user.name }}</td>
                        <td>{{ user.company }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ user.department }}</td>
                        <td>
                            {% if user.role == 'admin' %}
                                <span class="badge" style="background:#dc3545; color:white;">🛡️ Admin</span>
                            {% else %}
                                <span class="badge" style="background:#6c757d; color:white;">Usuário</span>
                            {% endif %}
                        </td>
                        <td>
                            <div class="flex gap-8">
                                <a href="{{ url_for('employee_edit', user_id=user.id) }}" class="btn btn-primary btn-sm">Editar</a>
                                <form method="post" action="{{ url_for('employee_delete', user_id=user.id) }}" style="display:inline;">
                                    <button type="submit" class="btn btn-danger btn-sm" onclick="return confirm('Excluir este cadastro?')">Excluir</button>
                                </form>
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="6" class="text-center">Nenhum colaborador cadastrado.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

        'employee_form.html': '''{% extends "base.html" %}
{% block title %}{{ 'Editar' if action=='edit' else 'Novo' }} Cadastro{% endblock %}
{% block page_title %}{{ 'Editar' if action=='edit' else 'Novo' }} Cadastro{% endblock %}
{% block content %}
<div class="card" style="max-width:600px; margin:0 auto;">
    <div class="card-body">
        <form method="post">
            <div class="form-group"><label>Nome</label><input type="text" name="name" class="form-control" value="{{ user.name if user else '' }}" required></div>
            <div class="form-row">
                <div class="form-group"><label>Empresa</label><input type="text" name="company" class="form-control" value="{{ user.company if user else '' }}" required></div>
                <div class="form-group"><label>Diretoria/Departamento</label><input type="text" name="department" class="form-control" value="{{ user.department if user else '' }}" required></div>
            </div>
            <div class="form-group"><label>E-mail</label><input type="email" name="email" class="form-control" value="{{ user.email if user else '' }}" required></div>
            <div class="form-group">
                <label>Perfil de acesso</label>
                <select name="role" class="form-control">
                    <option value="user" {% if not user or user.role == 'user' %}selected{% endif %}>Usuário</option>
                    <option value="admin" {% if user and user.role == 'admin' %}selected{% endif %}>Administrador</option>
                </select>
            </div>
            <div class="flex" style="justify-content:flex-end; margin-top:16px;">
                <a href="{{ url_for('employees') }}" class="btn btn-secondary">Cancelar</a>
                <button type="submit" class="btn btn-primary">Salvar</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

        'events.html': '''{% extends "base.html" %}
{% block title %}Eventos - Energisa{% endblock %}
{% block page_title %}Eventos / Palestras{% endblock %}
{% block page_sub %}Cadastro de eventos{% endblock %}
{% block content %}
<div class="flex-between mb-20">
    <div></div>
    <div class="flex gap-8">
        <form method="post" action="{{ url_for('manual_update') }}" style="display:inline;">
            <button type="submit" class="btn btn-warning">🔄 Atualizar Eventos</button>
        </form>
        <a href="{{ url_for('event_add') }}" class="btn btn-success">+ Novo Evento</a>
    </div>
</div>
<div class="card">
    <div class="card-header"><h2>Lista de Eventos</h2></div>
    <div class="card-body">
        <div class="table-wrapper">
            <table class="table">
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Origem</th>
                        <th>Data</th>
                        <th>Horário</th>
                        <th>Tipo</th>
                        <th>Local</th>
                        <th>País</th>
                        <th>Link Evento</th>
                        <th>Link Inscrição</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for ev in events %}
                    <tr>
                        <td>{{ ev.title }}</td>
                        <td>
                            {% if ev.source == 'auto' %}
                                <span class="badge" style="background:#0d6efd; color:white;" title="Encontrado automaticamente via web search">🤖 Auto</span>
                            {% else %}
                                <span class="badge" style="background:#6c757d; color:white;" title="Cadastrado manualmente">✋ Manual</span>
                            {% endif %}
                        </td>
                        <td>{{ ev.date.strftime('%d/%m/%Y') }}</td>
                        <td>{{ ev.time or '-' }}</td>
                        <td><span class="badge">{{ ev.event_type or 'Geral' }}</span></td>
                        <td>{{ ev.location or '-' }}</td>
                        <td>{{ ev.country or '-' }}</td>
                        <td>
                            {% if ev.site %}
                                <div class="link-copy">
                                    <a href="{{ ev.site }}" target="_blank">🌐</a>
                                    <span class="url-text">{{ ev.site }}</span>
                                </div>
                            {% else %}-{% endif %}
                        </td>
                        <td>
                            {% if ev.link %}
                                <div class="link-copy">
                                    <a href="{{ ev.link }}" target="_blank">📝</a>
                                    <span class="url-text">{{ ev.link }}</span>
                                </div>
                            {% else %}-{% endif %}
                        </td>
                        <td>
                            <div class="flex gap-8">
                                <a href="{{ url_for('event_talks', event_id=ev.id) }}" class="btn btn-secondary btn-sm" title="Cadastrar/gerenciar palestras">📋+</a>
                                <a href="{{ url_for('event_edit', event_id=ev.id) }}" class="btn btn-primary btn-sm">Editar</a>
                                <form method="post" action="{{ url_for('event_delete', event_id=ev.id) }}" style="display:inline;">
                                    <button type="submit" class="btn btn-danger btn-sm" onclick="return confirm('Excluir este evento e todas as inscrições?')">Excluir</button>
                                </form>
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="10" class="text-center">Nenhum evento cadastrado.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

        'event_form.html': '''{% extends "base.html" %}
{% block title %}{{ 'Editar' if action=='edit' else 'Novo' }} Evento{% endblock %}
{% block page_title %}{{ 'Editar' if action=='edit' else 'Novo' }} Evento{% endblock %}
{% block content %}
<div class="card" style="max-width:700px; margin:0 auto;">
    <div class="card-body">
        <form method="post">
            <div class="form-group"><label>Título</label><input type="text" name="title" class="form-control" value="{{ event.title if event else '' }}" required></div>
            <div class="form-group"><label>Descrição</label><textarea name="description" class="form-control" rows="3">{{ event.description if event else '' }}</textarea></div>
            <div class="form-row">
                <div class="form-group"><label>Data</label><input type="date" name="date" class="form-control" value="{{ event.date.strftime('%Y-%m-%d') if event else '' }}" required></div>
                <div class="form-group"><label>Horário</label><input type="time" name="time" class="form-control" value="{{ event.time if event else '' }}"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>Estado / Cidade</label><input type="text" name="location" class="form-control" value="{{ event.location if event else '' }}" placeholder="Ex: São Paulo"></div>
                <div class="form-group"><label>País</label><input type="text" name="country" class="form-control" value="{{ event.country if event else '' }}" placeholder="Ex: Brasil"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>Link do Evento (site oficial)</label><input type="url" name="site" class="form-control" value="{{ event.site if event else '' }}" placeholder="https://..."></div>
                <div class="form-group"><label>Link da Inscrição</label><input type="url" name="link" class="form-control" value="{{ event.link if event else '' }}" placeholder="https://..."></div>
            </div>
            <div class="form-group"><label>Tipo do evento</label><input type="text" name="event_type" class="form-control" value="{{ event.event_type if event else '' }}" placeholder="Ex: Renovável, Eólica, Distribuição..."></div>
            <div class="flex" style="justify-content:flex-end; margin-top:16px;">
                <a href="{{ url_for('events') }}" class="btn btn-secondary">Cancelar</a>
                <button type="submit" class="btn btn-primary">Salvar</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

        'event_talks.html': '''{% extends "base.html" %}
{% block title %}Palestras - {{ event.title }}{% endblock %}
{% block page_title %}Palestras: {{ event.title }}{% endblock %}
{% block page_sub %}{{ event.date.strftime('%d/%m/%Y') }}{% endblock %}
{% block content %}
<div class="flex-between mb-20">
    <a href="{{ url_for('events') }}" class="btn btn-secondary">← Voltar pra Eventos</a>
</div>

<div class="card" style="max-width:700px; margin:0 auto 16px auto;">
    <div class="card-header"><h2>+ Nova palestra</h2></div>
    <div class="card-body">
        <form method="post" action="{{ url_for('event_talk_add', event_id=event.id) }}">
            <div class="form-group"><label>Título</label><input type="text" name="title" class="form-control" required></div>
            <div class="form-row">
                <div class="form-group"><label>Palestrante</label><input type="text" name="speaker" class="form-control"></div>
                <div class="form-group"><label>Horário</label><input type="text" name="time" class="form-control" placeholder="Ex: 14:00"></div>
            </div>
            <div class="form-group"><label>Descrição</label><textarea name="description" class="form-control" rows="2"></textarea></div>
            <div class="flex" style="justify-content:flex-end;">
                <button type="submit" class="btn btn-primary">Adicionar palestra</button>
            </div>
        </form>
    </div>
</div>

<div class="card" style="max-width:700px; margin:0 auto;">
    <div class="card-header"><h2>Palestras cadastradas ({{ talks|length }})</h2></div>
    <div class="card-body">
        {% if talks %}
            {% for talk in talks %}
                <div class="talk-item" style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                    <div>
                        <span class="talk-time">{{ talk.time }}</span>
                        <strong>{{ talk.title }}</strong>
                        {% if talk.speaker %}<span style="font-size:12px; color:var(--text-2);"> - {{ talk.speaker }}</span>{% endif %}
                        <div style="font-size:12px; color:var(--text-3);">{{ talk.description }}</div>
                    </div>
                    <form method="post" action="{{ url_for('event_talk_delete', talk_id=talk.id) }}" onsubmit="return confirm('Remover essa palestra? As inscrições nela também serão removidas.');">
                        <button type="submit" class="btn btn-danger btn-sm">Excluir</button>
                    </form>
                </div>
            {% endfor %}
        {% else %}
            <p style="color:var(--text-3);">
                Nenhuma palestra cadastrada ainda para esse evento.
                {% if event.site %}<br><a href="{{ event.site }}" target="_blank">Ver programação completa no site do evento →</a>{% endif %}
            </p>
        {% endif %}
    </div>
</div>
{% endblock %}''',

        'event_register_self.html': '''{% extends "base.html" %}
{% block title %}Inscrição no Evento{% endblock %}
{% block page_title %}Inscrição no Evento{% endblock %}
{% block page_sub %}Confirme sua participação{% endblock %}
{% block content %}
<div style="max-width:450px; margin:0 auto;">
    <div class="card">
        <div class="card-header"><h2>{{ event.title }}</h2></div>
        <div class="card-body">
            <form method="post" action="{{ url_for('event_register_self', event_id=event.id) }}">
                <div class="form-group">
                    <label>Nome</label>
                    <input type="text" class="form-control" value="{{ current_user.name }}" readonly style="background:var(--surface-2); color:var(--text-3);">
                </div>
                <div class="form-group">
                    <label>Nome do evento</label>
                    <input type="text" class="form-control" value="{{ event.title }}" readonly style="background:var(--surface-2); color:var(--text-3);">
                </div>
                <div class="form-group">
                    <label>Data</label>
                    <input type="text" class="form-control" value="{{ event.date.strftime('%d/%m/%Y') }}" readonly style="background:var(--surface-2); color:var(--text-3);">
                </div>
                <div class="form-group">
                    <label>Nome do hotel</label>
                    <input type="text" name="hotel_name" class="form-control" placeholder="Onde você vai se hospedar (opcional)">
                </div>
                <div class="flex" style="justify-content:flex-end; gap:8px; margin-top:16px;">
                    <a href="{{ url_for('dashboard', event_id=event.id) }}" class="btn btn-secondary">Cancelar</a>
                    <button type="submit" class="btn btn-primary">Confirmar inscrição</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}''',


        'registrations.html': '''{% extends "base.html" %}
{% block title %}Inscrições - Energisa{% endblock %}
{% block page_title %}Inscrições em Palestras{% endblock %}
{% block page_sub %}Colaboradores inscritos e evidências{% endblock %}
{% block content %}
<div class="card" style="margin-bottom:16px;">
    <div class="card-header"><h2>Filtros</h2></div>
    <div class="card-body">
        <form method="get" action="{{ url_for('registrations') }}" style="display:flex; gap:8px; flex-wrap:wrap; align-items:flex-end;">
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Colaborador</label>
                <select name="f_colaborador" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for nome in opcoes_colaborador %}
                        <option value="{{ nome }}" {% if f_colaborador == nome %}selected{% endif %}>{{ nome }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Evento</label>
                <select name="f_evento" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for titulo in opcoes_evento %}
                        <option value="{{ titulo }}" {% if f_evento == titulo %}selected{% endif %}>{{ titulo }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Palestra</label>
                <select name="f_palestra" class="form-control" style="font-size:12px;">
                    <option value="">Todas</option>
                    {% for titulo in opcoes_palestra %}
                        <option value="{{ titulo }}" {% if f_palestra == titulo %}selected{% endif %}>{{ titulo }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Palestrante</label>
                <select name="f_palestrante" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for nome in opcoes_palestrante %}
                        <option value="{{ nome }}" {% if f_palestrante == nome %}selected{% endif %}>{{ nome }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Dia</label>
                <select name="f_dia" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for dia in opcoes_dia %}
                        <option value="{{ dia }}" {% if f_dia == dia|string %}selected{% endif %}>{{ "%02d"|format(dia) }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Mês</label>
                <select name="f_mes" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for mes in opcoes_mes %}
                        <option value="{{ mes }}" {% if f_mes == mes|string %}selected{% endif %}>{{ meses_nomes[mes] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Ano</label>
                <select name="f_ano" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for ano in opcoes_ano %}
                        <option value="{{ ano }}" {% if f_ano == ano|string %}selected{% endif %}>{{ ano }}</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Filtrar</button>
            {% if f_colaborador or f_palestra or f_evento or f_dia or f_mes or f_ano or f_palestrante %}
                <a href="{{ url_for('registrations') }}" class="btn btn-secondary btn-sm">Limpar</a>
            {% endif %}
        </form>
    </div>
</div>
<div class="card">
    <div class="card-header"><h2>Lista de Inscrições ({{ registrations|length }})</h2></div>
    <div class="card-body">
        <div class="table-wrapper">
            <table class="table">
                <thead><tr><th>Colaborador</th><th>Palestra</th><th>Evento</th><th>Data inscrição</th><th>Evidência</th><th>Ações</th></tr></thead>
                <tbody>
                    {% for reg in registrations %}
                    {% set pode_incluir = current_user.is_admin() or reg.user_id == current_user.id %}
                    {% set pode_excluir = current_user.is_admin() or reg.evidence_uploaded_by == current_user.id %}
                    <tr>
                        <td>{{ reg.user.name }} <span style="font-size:11px; color:var(--text-3);">({{ reg.user.department }})</span></td>
                        <td>{{ reg.talk.title }}</td>
                        <td>{{ reg.talk.event.title }}</td>
                        <td>{{ reg.registration_date.strftime('%d/%m/%Y %H:%M') }}</td>
                        <td>
                            {% if reg.evidence_path %}
                                <span class="badge" style="background:#28a745; color:white;">✅ Anexada</span>
                            {% else %}
                                <span class="badge" style="background:#6c757d; color:white;">Sem evidência</span>
                            {% endif %}
                        </td>
                        <td>
                            <div class="flex gap-8" style="flex-wrap:nowrap; align-items:flex-start; overflow-x:auto; padding-top:2px;">
                                {% if pode_incluir %}
                                    <form method="post" action="{{ url_for('talk_evidence_upload', reg_id=reg.id) }}" enctype="multipart/form-data" style="display:flex; flex-direction:column; gap:2px; flex-shrink:0;">
                                        <div style="display:flex; gap:4px; align-items:center;">
                                            <input type="file" name="evidence_file" id="file_{{ reg.id }}" required style="display:none;" onchange="this.closest('form').querySelector('.file-label').textContent = this.files.length ? this.files[0].name : 'Nenhum arquivo escolhido';">
                                            <label for="file_{{ reg.id }}" class="btn btn-secondary btn-sm" style="cursor:pointer; flex-shrink:0; white-space:nowrap; margin:0;">📎 Escolher arquivo</label>
                                            <button type="submit" class="btn btn-primary btn-sm" title="Incluir evidência" style="flex-shrink:0; white-space:nowrap;">➕ {{ 'Substituir' if reg.evidence_path else 'Incluir' }}</button>
                                        </div>
                                        <span class="file-label" style="font-size:9px; color:var(--text-3); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:150px;">Nenhum arquivo escolhido</span>
                                    </form>
                                {% endif %}
                                {% if reg.evidence_path %}
                                    <a href="{{ url_arquivo(reg.evidence_path) }}" target="_blank" class="btn btn-secondary btn-sm" title="Visualizar" style="flex-shrink:0; white-space:nowrap;">👁️ Visualizar</a>
                                    <a href="{{ url_arquivo(reg.evidence_path) }}" download class="btn btn-secondary btn-sm" title="Baixar" style="flex-shrink:0; white-space:nowrap;">⬇️ Baixar</a>
                                    {% if pode_excluir %}
                                        <form method="post" action="{{ url_for('talk_evidence_delete', reg_id=reg.id) }}" onsubmit="return confirm('Excluir essa evidência?');" style="display:inline; flex-shrink:0;">
                                            <button type="submit" class="btn btn-danger btn-sm" title="Excluir evidência" style="white-space:nowrap;">❌ Excluir</button>
                                        </form>
                                    {% endif %}
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="6" class="text-center">Nenhuma inscrição em palestras encontrada.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

        'relatorio_inscritos.html': '''{% extends "base.html" %}
{% block title %}Relatório de Inscritos{% endblock %}
{% block page_title %}Relatório de Inscritos por Evento{% endblock %}
{% block page_sub %}Filtre e exporte a lista{% endblock %}
{% block content %}
<div class="card" style="margin-bottom:16px;">
    <div class="card-header"><h2>Filtros</h2></div>
    <div class="card-body">
        <form method="get" action="{{ url_for('relatorio_inscritos') }}" style="display:flex; gap:8px; flex-wrap:wrap; align-items:flex-end;">
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Evento</label>
                <select name="r_evento" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for e in opcoes_evento %}
                        <option value="{{ e }}" {% if r_evento == e %}selected{% endif %}>{{ e }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Participante</label>
                <select name="r_nome" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for n in opcoes_nome %}
                        <option value="{{ n }}" {% if r_nome == n %}selected{% endif %}>{{ n }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Mês</label>
                <select name="r_mes" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for m in range(1, 13) %}
                        <option value="{{ m }}" {% if r_mes == m|string %}selected{% endif %}>{{ "%02d"|format(m) }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Ano</label>
                <select name="r_ano" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for a in anos_disponiveis %}
                        <option value="{{ a }}" {% if r_ano == a|string %}selected{% endif %}>{{ a }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">Estado</label>
                <select name="r_uf" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for uf in opcoes_uf %}
                        <option value="{{ uf }}" {% if r_uf == uf %}selected{% endif %}>{{ uf }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:11px;">País</label>
                <select name="r_pais" class="form-control" style="font-size:12px;">
                    <option value="">Todos</option>
                    {% for p in opcoes_pais %}
                        <option value="{{ p }}" {% if r_pais == p %}selected{% endif %}>{{ p }}</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Filtrar</button>
            {% if r_evento or r_nome or r_mes or r_ano or r_uf or r_pais %}
                <a href="{{ url_for('relatorio_inscritos') }}" class="btn btn-secondary btn-sm">Limpar</a>
            {% endif %}
        </form>
    </div>
</div>

<div class="card">
    <div class="card-header" style="flex-wrap:wrap; gap:8px;">
        <h2>Inscritos ({{ registros|length }})</h2>
        <div class="flex gap-8">
            <a href="{{ url_for('relatorio_inscritos_xlsx', **request.args) }}" class="btn btn-secondary btn-sm">⬇️ XLSX</a>
            <a href="{{ url_for('relatorio_inscritos_pdf', **request.args) }}" class="btn btn-secondary btn-sm">⬇️ PDF</a>
        </div>
    </div>
    <div class="card-body">
        <div class="table-wrapper">
            <table class="table">
                <thead><tr><th>Colaborador</th><th>Departamento</th><th>Evento</th><th>Data</th><th>Local</th><th>Estado</th><th>País</th><th>Hotel</th></tr></thead>
                <tbody>
                    {% for r in registros %}
                    <tr>
                        <td>{{ r.user.name }}</td>
                        <td>{{ r.user.department }}</td>
                        <td>{{ r.event.title }}</td>
                        <td>{{ r.event.date.strftime('%d/%m/%Y') }}</td>
                        <td>{{ r.event.location or '-' }}</td>
                        <td>{{ uf_por_cidade(r.event.location) or '-' }}</td>
                        <td>{{ r.event.country or '-' }}</td>
                        <td>{{ r.hotel_name or '-' }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="8" class="text-center">Nenhum inscrito encontrado para esse filtro.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',

        'registration_form.html': '''{% extends "base.html" %}
{% block title %}Nova Inscrição{% endblock %}
{% block page_title %}Nova Inscrição{% endblock %}
{% block content %}
<div class="card" style="max-width:600px; margin:0 auto;">
    <div class="card-body">
        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label>Colaborador</label>
                <select name="user_id" class="form-control" required>
                    <option value="">Selecione...</option>
                    {% for u in users %}
                    <option value="{{ u.id }}">{{ u.name }} ({{ u.email }})</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Palestra / Evento</label>
                <select name="event_id" class="form-control" required>
                    <option value="">Selecione...</option>
                    {% for ev in events %}
                    <option value="{{ ev.id }}">{{ ev.title }} - {{ ev.date.strftime('%d/%m/%Y') }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Evidência (PDF, PPT, TXT, XLSX, PNG, ZIP, JPEG, PPTX)</label>
                <input type="file" name="evidence_file" class="form-control" accept=".pdf,.ppt,.pptx,.txt,.xlsx,.png,.zip,.jpeg,.jpg">
            </div>
            <div class="flex" style="justify-content:flex-end; margin-top:16px;">
                <a href="{{ url_for('registrations') }}" class="btn btn-secondary">Cancelar</a>
                <button type="submit" class="btn btn-primary">Inscrever</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}'''
    }

    for filename, content in templates.items():
        if not IS_VERCEL:
            path = os.path.join('templates', filename)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📄 Template criado: {filename}")
    return templates


# ============================================================
# INICIALIZAÇÃO DO BANCO DE DADOS
# ============================================================
def init_db():
    with app.app_context():
        db.create_all()
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(events)"))
                columns = [row[1] for row in result]
                if 'location' not in columns:
                    conn.execute(text("ALTER TABLE events ADD COLUMN location VARCHAR(100)"))
                    print("➕ location adicionada")
                if 'country' not in columns:
                    conn.execute(text("ALTER TABLE events ADD COLUMN country VARCHAR(100)"))
                    print("➕ country adicionada")
                if 'source' not in columns:
                    conn.execute(text("ALTER TABLE events ADD COLUMN source VARCHAR(20) DEFAULT 'manual'"))
                    print("➕ source adicionada")
                if 'source_url' not in columns:
                    conn.execute(text("ALTER TABLE events ADD COLUMN source_url VARCHAR(500)"))
                    print("➕ source_url adicionada")
                if 'updated_at' not in columns:
                    conn.execute(text("ALTER TABLE events ADD COLUMN updated_at DATETIME"))
                    print("➕ updated_at adicionada")
                if 'normalized_key' not in columns:
                    conn.execute(text("ALTER TABLE events ADD COLUMN normalized_key VARCHAR(300)"))
                    print("➕ normalized_key (events) adicionada")
                conn.commit()
        except Exception as e:
            # IMPORTANTE: nunca apagamos a tabela events automaticamente aqui.
            # Um erro de migração não pode virar perda de dados — só avisamos e seguimos,
            # deixando os dados como estão pra investigação manual se precisar.
            print(f"⚠️ Erro ao adicionar colunas em events: {e}")
            print("   Nenhum dado foi apagado. Verifique manualmente se precisar.")

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(talks)"))
                columns = [row[1] for row in result]
                if columns and 'normalized_key' not in columns:
                    conn.execute(text("ALTER TABLE talks ADD COLUMN normalized_key VARCHAR(300)"))
                    print("➕ normalized_key (talks) adicionada")
                    conn.commit()
        except Exception as e:
            print(f"⚠️ Erro ao adicionar normalized_key em talks: {e}")

        # Limpa duplicatas que já existiam ANTES da chave única existir — precisa
        # rodar antes de criar o índice único, senão a criação do índice falha.
        try:
            _deduplicar_eventos_auto()
        except Exception as e:
            print(f"⚠️ Erro ao deduplicar eventos/palestras: {e}")

        # Preenche a chave de quem ainda não tem (inclusive eventos/palestras manuais,
        # que a deduplicação automática não mexe)
        try:
            for e in Event.query.filter(Event.normalized_key.is_(None)).all():
                e.normalized_key = _event_key(e.title, e.date)
            for t in Talk.query.filter(Talk.normalized_key.is_(None)).all():
                t.normalized_key = _talk_key(t.event_id, t.title)
            db.session.commit()
        except Exception as e:
            print(f"⚠️ Erro ao preencher normalized_key: {e}")

        # Só agora cria os índices únicos — depois de garantir que não há mais duplicata.
        # Se ainda houver alguma (ex: duplicata manual que a limpeza automática não mescla),
        # a criação falha e avisa no log, mas não trava o resto da aplicação.
        try:
            with db.engine.connect() as conn:
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_events_normalized_key ON events(normalized_key)"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_talks_normalized_key ON talks(normalized_key)"))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Não foi possível criar o índice único (provável duplicata manual residual): {e}")
            print("   Verifique manualmente eventos/palestras com nome e data repetidos.")

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                if 'must_change_password' not in columns:
                    # Usuários já existentes (criados antes dessa coluna existir) não são forçados
                    # a trocar a senha retroativamente — só os cadastrados a partir de agora.
                    conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0"))
                    print("➕ must_change_password adicionada")
                if 'role' not in columns:
                    # Usuários já existentes viram 'user' por padrão — promover manualmente quem precisar.
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
                    print("➕ role adicionada")
                conn.commit()
        except Exception as e:
            print(f"⚠️ Erro ao adicionar coluna must_change_password/role: {e}")

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(talk_registrations)"))
                columns = [row[1] for row in result]
                if columns:  # só migra se a tabela já existir (create_all cuida do resto)
                    if 'evidence_path' not in columns:
                        conn.execute(text("ALTER TABLE talk_registrations ADD COLUMN evidence_path VARCHAR(300)"))
                        print("➕ evidence_path adicionada")
                    if 'evidence_uploaded_by' not in columns:
                        conn.execute(text("ALTER TABLE talk_registrations ADD COLUMN evidence_uploaded_by INTEGER"))
                        print("➕ evidence_uploaded_by adicionada")
                    conn.commit()
        except Exception as e:
            print(f"⚠️ Erro ao adicionar colunas de evidência em talk_registrations: {e}")

        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(registrations)"))
                columns = [row[1] for row in result]
                if columns and 'hotel_name' not in columns:
                    conn.execute(text("ALTER TABLE registrations ADD COLUMN hotel_name VARCHAR(200)"))
                    print("➕ hotel_name adicionada")
                    conn.commit()
        except Exception as e:
            print(f"⚠️ Erro ao adicionar coluna hotel_name em registrations: {e}")

        admin = User.query.filter_by(email='admin@energisa.com.br').first()
        if not admin:
            admin = User(
                name='Administrador',
                registration_number='ADMIN001',
                company='Energisa',
                email='admin@energisa.com.br',
                department='TI',
                role='admin'
            )
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("👤 Admin criado")
        elif admin.role != 'admin':
            # Garante que a conta admin@energisa.com.br sempre tenha perfil admin,
            # mesmo em bancos migrados de uma versão anterior à existência de perfis.
            admin.role = 'admin'
            db.session.commit()
            print("🛡️ Perfil da conta admin@energisa.com.br corrigido para 'admin'")

        if Event.query.count() == 0:
            print("📅 Gerando eventos iniciais...")
            update_events()
        else:
            print(f"📅 {Event.query.count()} eventos já cadastrados.")


# ============================================================
# EXECUÇÃO
# ============================================================
# create_templates() e init_db() rodam sempre que o módulo é carregado — inclusive quando a
# Vercel importa esse arquivo pra servir como função serverless (nesse caso o bloco
# "if __name__ == '__main__'" abaixo nunca executa, já que a Vercel não roda o arquivo
# diretamente, só importa a variável "app").
_TEMPLATES_DICT = create_templates()

# Na Vercel não dá pra escrever a pasta templates/ em disco (sistema de arquivos read-only
# fora de /tmp), então registramos um DictLoader com os templates em memória como fallback.
# Localmente continua funcionando como antes, lendo da pasta templates/ normalmente —
# o ChoiceLoader tenta o carregador padrão primeiro, só cai pro DictLoader se não achar o arquivo.
from jinja2 import ChoiceLoader, DictLoader
app.jinja_loader = ChoiceLoader([app.jinja_loader, DictLoader(_TEMPLATES_DICT)])

init_db()

if __name__ == '__main__':
    if IS_VERCEL:
        pass  # nunca deveria cair aqui na Vercel, mas por segurança não inicia o scheduler/dev server
    elif not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        scheduler.add_job(refresh_events, 'cron', hour=1, minute=0)
        scheduler.add_job(refresh_events, 'cron', hour=12, minute=0)
        scheduler.start()
        print("⏰ Agendador iniciado (01:00 e 12:00) — só roda localmente, na Vercel isso é um Cron Job")

    if not IS_VERCEL:
        app.run(debug=True, host='0.0.0.0', port=8080)
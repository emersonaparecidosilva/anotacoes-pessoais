# database/connection.py
import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import datetime
from bson.objectid import ObjectId 

@st.cache_resource
def get_database():
    try:
        mongo_uri = st.secrets["mongodb"]["uri"]
        db_name = st.secrets["mongodb"]["db_name"]
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        return client[db_name]
    except Exception as e:
        st.error(f"Erro ao conectar ao MongoDB Atlas: {e}")
        return None

def salvar_anotacao(titulo, conteudo, tags, arquivos_lista=None):
    """Insere uma nova anotação. 'arquivos_lista' agora guarda dicionários com nome e base64."""
    db = get_database()
    if db is None:
        return False
        
    colecao = db["anotacoes"]
    
    documento = {
        "titulo": titulo,
        "conteudo": conteudo,
        "tags": [tag.strip().lower() for tag in tags.split(",") if tag.strip()],
        "arquivos": arquivos_lista if arquivos_lista else [], # Lista de arquivos anexados
        "data_criacao": datetime.datetime.now(datetime.timezone.utc),
        "data_atualizacao": datetime.datetime.now(datetime.timezone.utc)
    }
    
    resultado = colecao.insert_one(documento)
    return resultado.inserted_id

def atualizar_anotacao(id_nota, titulo, conteudo, tags, arquivos_lista=None):
    """Atualiza uma nota existente no MongoDB."""
    db = get_database()
    if db is None:
        return False
        
    colecao = db["anotacoes"]
    
    dados_atualizados = {
        "titulo": titulo,
        "conteudo": conteudo,
        "tags": [tag.strip().lower() for tag in tags.split(",") if tag.strip()],
        "data_atualizacao": datetime.datetime.now(datetime.timezone.utc)
    }
    
    # Se uma nova lista de arquivos for enviada, ela substitui a antiga
    if arquivos_lista is not None:
        dados_atualizados["arquivos"] = arquivos_lista
        
    resultado = colecao.update_one(
        {"_id": ObjectId(id_nota)},
        {"$set": dados_atualizados}
    )
    return resultado.modified_count > 0

def buscar_anotacoes_filtradas(termo_busca=None, tag_busca=None, data_busca=None):
    db = get_database()
    if db is None:
        return []
        
    query = {}
    
    if termo_busca:
        query["$or"] = [
            {"titulo": {"$regex": termo_busca, "$options": "i"}},
            {"conteudo": {"$regex": termo_busca, "$options": "i"}}
        ]
        
    if tag_busca:
        query["tags"] = tag_busca.strip().lower()
        
    if data_busca:
        inicio_dia = datetime.datetime.combine(data_busca, datetime.time.min)
        fim_dia = datetime.datetime.combine(data_busca, datetime.time.max)
        query["data_criacao"] = {"$gte": inicio_dia, "$lte": fim_dia}
        
    return list(db["anotacoes"].find(query).sort("data_criacao", -1))

def excluir_anotacao(id_nota):
    """
    Remove definitivamente uma anotação do MongoDB Atlas usando o ID.
    """
    db = get_database()
    if db is None:
        return False
        
    colecao = db["anotacoes"]
    
    # Executa a remoção baseada no ObjectId do documento
    resultado = colecao.delete_one({"_id": ObjectId(id_nota)})
    return resultado.deleted_count > 0

def registrar_log_auditoria(evento, detalhes, ip_usuario="desconhecido"):
    """
    Registra um evento de segurança ou alteração crítica na coleção de auditoria.
    """
    db = get_database()
    if db is None:
        return False
        
    colecao = db["auditoria_acesso"]
    
    log = {
        "evento": evento,        # ex: "login_sucesso", "login_falha_senha", "nota_excluida"
        "detalhes": detalhes,    # Descrição do que aconteceu
        "ip_origem": ip_usuario, # IP do cliente fornecido pelo Streamlit
        "data_evento": datetime.datetime.now(datetime.timezone.utc)
    }
    
    colecao.insert_one(log)
    return True

def buscar_logs_auditoria(limite=50):
    """
    Retorna os últimos logs de auditoria registrados, ordenados do mais recente para o mais antigo.
    """
    db = get_database()
    if db is None:
        return []
        
    colecao = db["auditoria_acesso"]
    # Busca os registros e ordena pela data_evento decrescente (-1)
    return list(colecao.find().sort("data_evento", -1).limit(limite))
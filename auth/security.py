# auth/security.py
import streamlit as st
import pyotp
import qrcode
from io import BytesIO

def verificar_senha(senha_digitada):
    """
    Verifica se a senha digitada corresponde à cadastrada no secrets.
    """
    senha_correta = st.secrets["auth"]["senha_painel"]
    return senha_digitada == senha_correta

def obter_provedor_2fa():
    """
    Retorna o objeto TOTP configurado com a chave do secrets.
    """
    segredo_32 = st.secrets["auth"]["chave_2fa_master"]
    # CORREÇÃO: O argumento correto no construtor é 'issuer'
    return pyotp.TOTP(segredo_32, issuer="Portal de Anotações")

def verificar_codigo_2fa(codigo_digitado):
    """
    Valida se o código de 6 dígitos inserido está correto para o momento atual.
    """
    totp = obter_provedor_2fa()
    return totp.verify(codigo_digitado)

def gerar_qrcode_setup():
    """
    Gera a imagem do QR Code para que você possa escanear no Google Authenticator
    apenas na primeira configuração do sistema.
    """
    totp = obter_provedor_2fa()
    # Aqui o 'issuer_name' continua igual, pois identifica o provedor na URL do QR Code
    url_auth = totp.provisioning_uri(name="emerson@admin", issuer_name="Portal de Anotações")
    
    # Transforma a URL em uma imagem do QR Code em memória
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_auth)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
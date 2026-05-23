# app.py
import streamlit as st
from auth.security import verificar_senha, verificar_codigo_2fa, gerar_qrcode_setup
from zoneinfo import ZoneInfo
import base64
from database.connection import salvar_anotacao, buscar_anotacoes_filtradas, atualizar_anotacao, excluir_anotacao

st.set_page_config(
    page_title="Meu Portal de Anotações", 
    page_icon="🔒", 
    layout="wide" 
)

# Inicializa o estado de login caso não exista
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "passo_senha_ok" not in st.session_state:
    st.session_state.passo_senha_ok = False

def tela_login():
    st.title("🔒 Acesso ao Portal")
    st.subheader("Este é um ambiente privado de anotações.")
    
    # ETAPA 1: Validação da Senha
    if not st.session_state.passo_senha_ok:
        with st.form("form_senha"):
            senha = st.text_input("Digite a senha master:", type="password")
            botao_senha = st.form_submit_button("Continuar")
            
            if botao_senha:
                if verificar_senha(senha):
                    st.session_state.passo_senha_ok = True
                    st.rerun()
                else:
                    st.error("Senha incorreta. Acesso negado.")
                    
    # ETAPA 2: Validação do Código 2FA
    else:
        st.info("🔓 Senha correta! Agora insira o código de verificação do seu celular.")
        
        with st.form("form_2fa"):
            codigo_2fa = st.text_input("Código de 6 dígitos (TOTP):", max_chars=6)
            botao_2fa = st.form_submit_button("Verificar e Entrar")
            
            if botao_2fa:
                if verificar_codigo_2fa(codigo_2fa):
                    st.session_state.autenticado = True
                    st.success("Autenticado com sucesso!")
                    st.rerun()
                else:
                    st.error("Código inválido ou expirado. Tente novamente.")
        
        # # Seção expansível para você ler o QR Code pela primeira vez
        # with st.expander("Primeira vez aqui? Escaneie o QR Code no seu celular"):
        #     st.write("Abra o Google Authenticator ou Authy, clique em adicionar código e escaneie a imagem abaixo:")
        #     img_qrcode = gerar_qrcode_setup()
        #     st.image(img_qrcode, width=250)
            
        if st.button("Voltar para tela de senha"):
            st.session_state.passo_senha_ok = False
            st.rerun()

# --- CONTROLE DE ROTA PRINCIPAL ---
if not st.session_state.autenticado:
    tela_login()
else:
    # --- PAINEL PRINCIPAL DO USUÁRIO ---
    st.title("📝 Meu Portal de Anotações")
    
    if st.sidebar.button("Sair do Portal"):
        st.session_state.autenticado = False
        st.session_state.passo_senha_ok = False
        st.rerun()
        
    # Inicializa estados de controle para edição se não existirem
    if "nota_em_edicao" not in st.session_state:
        st.session_state.nota_em_edicao = None

    # Se houver uma nota em edição, mostra o painel de edição no topo antes das abas
    if st.session_state.nota_em_edicao is not None:
        nota_atual = st.session_state.nota_em_edicao
        st.warning(f"✍️ Você está editando a nota: **{nota_atual['titulo']}**")
        
        with st.form("form_editar_nota"):
            ed_titulo = st.text_input("Título da Anotação:", value=nota_atual["titulo"])
            ed_conteudo = st.text_area("Conteúdo (pode colar texto aqui):", value=nota_atual["conteudo"], height=150)
            
            # Reconverte a lista de tags salva de volta para string separada por vírgula
            tags_string = ", ".join(nota_atual.get("tags", []))
            ed_tags = st.text_input("Tags (separadas por vírgula):", value=tags_string)
            
            st.info("Nota: Para preservar os anexos atuais, deixe o campo abaixo vazio. Para substituí-los, envie novos arquivos.")
            ed_arquivos = st.file_uploader("Substituir arquivos anexos (Opcional):", 
                                           type=["png", "jpg", "jpeg", "pdf", "docx", "xlsx"], 
                                           accept_multiple_files=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                submeteu_edicao = st.form_submit_button("Salvar Alterações")
            with col_b2:
                cancelou_edicao = st.form_submit_button("Cancelar Edição")
                
            if submeteu_edicao:
                lista_novos_arquivos = None
                if ed_arquivos:
                    lista_novos_arquivos = []
                    for arq in ed_arquivos:
                        bytes_arq = arq.read()
                        base64_arq = base64.b64encode(bytes_arq).decode('utf-8')
                        lista_novos_arquivos.append({"nome": arq.name, "tipo": arq.type, "base64": base64_arq})
                
                sucesso = atualizar_anotacao(nota_atual["_id"], ed_titulo, ed_conteudo, ed_tags, lista_novos_arquivos)
                if sucesso:
                    st.success("Anotação atualizada com sucesso!")
                    st.session_state.nota_em_edicao = None
                    st.rerun()
                else:
                    st.error("Nenhuma alteração foi modificada ou erro ao salvar.")
                    
            if cancelou_edicao:
                st.session_state.nota_em_edicao = None
                st.rerun()
                
        st.write("---")

    # Sistema de Abas padrão
    aba_criar, aba_buscar = st.tabs(["✨ Nova Anotação", "🔍 Buscar e Visualizar"])
    
    # --- ABA 1: CRIAR ANOTAÇÃO ---
    with aba_criar:
        st.subheader("Criar uma nova nota")
        
        with st.form("form_nova_nota", clear_on_submit=True):
            titulo_nota = st.text_input("Título da Anotação:")
            conteudo_nota = st.text_area("Conteúdo (Cole textos, links ou códigos aqui):", height=150)
            tags_nota = st.text_input("Tags (separadas por vírgula):", placeholder="ex: ideias, trabalho, pessoal")
            
            # NOVO: accept_multiple_files=True e inclusão de PDF/Office
            arquivos_enviados = st.file_uploader(
                "Adicionar Fotos, Prints, PDFs ou documentos Office (Opcional):", 
                type=["png", "jpg", "jpeg", "pdf", "docx", "xlsx"],
                accept_multiple_files=True
            )
            
            botao_salvar = st.form_submit_button("Salvar Anotação")
            
            if botao_salvar:
                if not titulo_nota or not conteudo_nota:
                    st.warning("Por favor, preencha o título e o conteúdo da sua nota!")
                else:
                    lista_arquivos_base64 = []
                    
                    # Processa cada um dos múltiplos arquivos enviados
                    if arquivos_enviados:
                        for arquivo in arquivos_enviados:
                            bytes_arq = arquivo.read()
                            string_base64 = base64.b64encode(bytes_arq).decode('utf-8')
                            lista_arquivos_base64.append({
                                "nome": arquivo.name,
                                "tipo": arquivo.type,
                                "base64": string_base64
                            })
                    
                    id_inserido = salvar_anotacao(titulo_nota, conteudo_nota, tags_nota, lista_arquivos_base64)
                    
                    if id_inserido:
                        st.success(f"Nota gravada com sucesso no MongoDB! ID: {id_inserido}")
                    else:
                        st.error("Falha ao salvar nota.")

    # --- ABA 2: BUSCAR E VISUALIZAR ANOTAÇÕES ---
    with aba_buscar:
        st.subheader("Filtrar suas anotações")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_texto = st.text_input("Buscar por termo (Título/Texto):", key="busca_txt")
        with col2:
            filtro_tag = st.text_input("Buscar por Tag específica:", key="busca_tag")
        with col3:
            ativar_data = st.checkbox("Filtrar por data específica", key="busca_dt_check")
            filtro_data = st.date_input("Escolha a data:", disabled=not ativar_data, key="busca_dt")
            
        data_param = filtro_data if ativar_data else None
        notas_encontradas = buscar_anotacoes_filtradas(filtro_texto, filtro_tag, data_param)
        
        st.markdown(f"**{len(notas_encontradas)}** anotação(ões) encontrada(s):")
        st.write("---")
        
        for nota in notas_encontradas:
            data_utc = nota["data_criacao"].replace(tzinfo=ZoneInfo("UTC"))
            data_local = data_utc.astimezone(ZoneInfo("America/Sao_Paulo"))
            data_formatada = data_local.strftime("%d/%m/%Y %H:%M")
            
            # REQUISITO: Exibição limpa em modo expansível (Título + Data no cabeçalho)
            label_expander = f"📌 {nota['titulo']} | 📅 {data_formatada}"
            
            with st.expander(label_expander, expanded=False):
                # Conteúdo do texto
                st.write(nota["conteudo"])
                
                # Tags
                if nota.get("tags"):
                    tags_linha = " ".join([f"`#{tag}`" for tag in nota["tags"]])
                    st.markdown(f"Tags: {tags_linha}")
                
                # Renderização/Download de múltiplos arquivos anexados
                if nota.get("arquivos"):
                    st.write("**Arquivos anexados:**")
                    for idx, arq in enumerate(nota["arquivos"]):
                        dados_totais = base64.b64decode(arq["base64"])
                        
                        if "image" in arq["tipo"]:
                            st.image(dados_totais, caption=arq["nome"], width='stretch')
                        else:
                            # Se for PDF ou Office, cria um botão nativo de download para você baixar o arquivo de volta intacto
                            st.download_button(
                                label=f"📥 Baixar {arq['nome']}",
                                data=dados_totais,
                                file_name=arq["nome"],
                                mime=arq["tipo"],
                                key=f"dl_{nota['_id']}_{idx}"
                            )
                
                # Botão para ativar a edição desta nota específica

                col_btn_ed, col_btn_ex = st.columns([1, 1])

                with col_btn_ed:
                    # Botão de Edição já existente
                    if st.button("✏️ Editar", key=f"btn_ed_{nota['_id']}", width='stretch'):
                        st.session_state.nota_em_edicao = nota
                        st.rerun()

                with col_btn_ex:
                    # Novo: Popover de confirmação para evitar cliques acidentais
                    with st.popover("🗑️ Excluir", width='stretch'):
                        st.warning("Tem certeza? Esta ação não pode ser desfeita.")
                        
                        # O botão real de exclusão fica oculto dentro do popover
                        if st.button("Sim, apagar nota", key=f"conf_ex_{nota['_id']}", type="primary", width='stretch'):
                            sucesso_exclusao = excluir_anotacao(nota["_id"])
                            
                            if sucesso_exclusao:
                                st.success("Nota excluída!")
                                st.rerun() # Atualiza a tela imediatamente para sumir com a nota
                            else:
                                st.error("Erro ao tentar excluir a nota.")
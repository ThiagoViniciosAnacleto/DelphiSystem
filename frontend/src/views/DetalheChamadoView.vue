<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// --- Estado Principal ---
const chamado = ref(null)
const logsTimeline = ref([])
const isLoading = ref(true)
const erro = ref(null)
const listaStatus = ref([])
const listaPrioridades = ref([])
const listaUsuarios = ref([])

// --- Estado para Formulários ---
const novoComentarioTexto = ref('')
const edicaoComentario = ref({ id: null, comentario: '' })

// --- Roteamento ---
const route = useRoute()
const router = useRouter()
const chamadoId = route.params.id

// --- 1. CONFIGURAÇÃO DA API ---
const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '');
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`,
};

// Função auxiliar para GET
const fetchData = async (endpoint) => {
    try {
        const res = await fetch(`${baseURL}${endpoint}`, { headers });
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || `Erro HTTP ${res.status} ao carregar ${endpoint}`);
        }
        return res.json();
    } catch (error) {
        console.error(`Erro ao carregar ${endpoint}:`, error);
        alert(`Erro ao carregar dados: ${error.message}`);
        throw error;
    }
};

// --- 2. FUNÇÕES DE DADOS (API) ---

async function carregarDadosDoChamado() {
    isLoading.value = true
    erro.value = null
    
    try {
        // Busca os 2 endpoints principais em paralelo
        // (Modificado para usar 'fetchData' em vez de 'api.get')
        const [
            resChamado, 
            resLogs,
            resListaStatus,     
            resListaPrioridades, 
            resListaUsuarios     
            ] = await Promise.all([
            fetchData(`/chamados/${chamadoId}`),
            fetchData(`/chamados/${chamadoId}/timeline`),
            fetchData('/status_chamado/'),
            fetchData('/prioridades/'),         
            fetchData('/usuarios/')
        ])

        // Armazena os dados (fetchData já retorna o .json())
        chamado.value = resChamado
        logsTimeline.value = resLogs
        listaStatus.value = resListaStatus
        listaPrioridades.value = resListaPrioridades
        listaUsuarios.value = resListaUsuarios

    } catch (err) {
        console.error("Erro ao buscar dados do chamado:", err)
        if (err.message.includes("404")) {
            erro.value = "Chamado não encontrado."
        } else {
            erro.value = "Falha ao carregar o histórico do chamado."
        }
    } finally {
        isLoading.value = false
    }
}

// --- 3. COMPUTED: O HISTÓRICO MESCLADO ---
const historicoOrdenado = computed(() => {
    if (!chamado.value) return []

    // Mapeamento dos comentários
    const comentarios = (chamado.value.interacoes || []).map(item => ({
        tipo: 'comentario',
        dataHora: item.data_interacao,
        autor: item.usuario ? item.usuario.nome : 'Usuário Desconhecido',
        conteudo: item.comentario,
        privado: item.privado,
        id: item.id,
        objetoOriginal: item,
        updated_at: item.updated_at
    }));

    // Mapeamento dos logs (usa a função de tradução)
    const logs = (logsTimeline.value || []).map(item => ({
        tipo: 'log',
        dataHora: item.data_hora,
        autor: item.usuario ? item.usuario.nome : 'Sistema',
        conteudo: formatarLogConteudo(item),
        id: item.id,
        objetoOriginal: item
    }));

// Mapeamento dos anexos
    const arquivos = (chamado.value.anexos || []).map(item => ({
        tipo: 'anexo',
        dataHora: item.data_upload, 
        autor: item.usuario ? item.usuario.nome : 'Usuário Desconhecido',
        conteudo: item.nome_arquivo_original,
        url: item.url,
        id: item.id
    }));

    const timeline = [...comentarios, ...logs, ...arquivos]

    return timeline.sort((a, b) => new Date(a.dataHora) - new Date(b.dataHora))
})

// --- 4. FUNÇÕES DE CRUD (AÇÕES) ---
// (Modificadas para usar 'fetch' em vez de 'api.post/put/delete')

async function enviarNovoComentario() {
    if (!novoComentarioTexto.value.trim()) return

    try {
        const res = await fetch(`${baseURL}/chamados/${chamadoId}/interacoes/`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                comentario: novoComentarioTexto.value,
                privado: false 
            })
        })
        if (!res.ok) { throw new Error(await res.json().then(d => d.detail)) }
        
        const resposta = await res.json()
        chamado.value.interacoes.push(resposta)
        novoComentarioTexto.value = '' 
    
    } catch (err) {
        console.error("Erro ao enviar comentário", err)
        alert("Falha ao salvar comentário.")
    }
}

function iniciarEdicao(comentario) {
    edicaoComentario.value.id = comentario.id
    edicaoComentario.value.comentario = comentario.conteudo
}

function cancelarEdicao() {
    edicaoComentario.value.id = null
    edicaoComentario.value.comentario = ''
}

/**
 * Atualiza um único campo do chamado principal (Status, Prioridade, etc.)
 * @param {string} campo - O nome do campo no backend (ex: "status_id")
 * @param {*} valor - O novo valor (ex: 3)
 */
async function atualizarCampoChamado(campo, valor) {
  // Cria o "corpo" (payload) da requisição
    const payload = {
        [campo]: valor
    }

    try {
        // Chama o endpoint PUT /chamados/{id}
        const res = await fetch(`${baseURL}/chamados/${chamadoId}`, {
            method: 'PUT',
            headers: headers,
            body: JSON.stringify(payload)
        })

    if (!res.ok) { 
        throw new Error(await res.json().then(d => d.detail || 'Erro desconhecido')) 
    }

    const chamadoAtualizado = await res.json()

    // --- A MÁGICA ACONTECE AQUI ---

    // 1. Atualiza o cabeçalho (ex: o nome do status)
    chamado.value = chamadoAtualizado 

    // 2. Busca os logs NOVAMENTE. 
    // A API (backend) acabou de criar um novo log (ex: "editou prioridade...").
    // Precisamos buscar a lista de logs atualizada para a timeline.
    logsTimeline.value = await fetchData(`/chamados/${chamadoId}/timeline`)

    // (Não precisamos recarregar as 'interacoes' ou 'anexos', 
    // pois o 'chamadoAtualizado' já os traz)

    } catch (err) {
        console.error(`Erro ao atualizar campo ${campo}:`, err)
        alert(`Falha ao atualizar o chamado: ${err.message}`)

    // Se falhar, recarregue os dados originais para reverter a mudança no dropdown
        carregarDadosDoChamado() 
    }
}

async function salvarEdicao() {
    if (!edicaoComentario.value.id) return
        
    try {
        const res = await fetch(`${baseURL}/interacoes/${edicaoComentario.value.id}`, {
            method: 'PUT',
            headers: headers,
            body: JSON.stringify({
                comentario: edicaoComentario.value.comentario
            })
        })
        if (!res.ok) { throw new Error(await res.json().then(d => d.detail)) }

        const resposta = await res.json()
        const index = chamado.value.interacoes.findIndex(c => c.id === edicaoComentario.value.id)
        if (index !== -1) {
            chamado.value.interacoes[index] = resposta
        }
        
        cancelarEdicao()
    
    } catch (err) {
        console.error("Erro ao salvar edição", err)
        alert("Falha ao salvar edição.")
    }
}

async function deletarComentario(comentarioId) {
    if (!confirm("Tem certeza que deseja deletar este comentário?")) return

    try {
        const res = await fetch(`${baseURL}/interacoes/${comentarioId}`, {
            method: 'DELETE',
            headers: headers
        })
        
        // O status 204 (No Content) do FastAPI não retorna JSON, então checamos assim
        if (res.status === 204) { 
            // Remove o comentário da lista local
            chamado.value.interacoes = chamado.value.interacoes.filter(c => c.id !== comentarioId)
        } else {
                if (!res.ok) { throw new Error(await res.json().then(d => d.detail)) }
        }
    
    } catch (err) {
        console.error("Erro ao deletar comentário", err)
        alert("Falha ao deletar comentário.")
    }
}

/**
 * "Traduz" um item de log bruto (ex: status_id=1) 
 * para um formato legível (ex: Status='Aberto')
 */
function formatarLogConteudo(logItem) {
    const { acao, campo, valor_antigo, valor_novo } = logItem;

    // Se não for uma atualização (ex: "Chamado criado"), só retorna o conteúdo.
    if (acao !== 'atualizacao') {
        return logItem.conteudo || acao; 
    }

    // 1. Traduz o NOME DO CAMPO
    const nomesCampos = {
        status_id: 'Status',
        prioridade_id: 'Prioridade',
        responsavel_acao_id: 'Responsável (Ação)'
        // Adicione outros campos aqui se precisar (ex: 'empresa_id')
    };
    const nomeCampoTraduzido = nomesCampos[campo] || campo; // Mantém o original se não achar tradução

    // 2. Define os valores padrão (IDs ou "vazio")
    let antigoTraduzido = valor_antigo || 'vazio';
    let novoTraduzido = valor_novo || 'vazio';

    // 3. Tenta traduzir os VALORES (IDs) usando as listas que já buscamos
    try {
        if (campo === 'status_id') {
            antigoTraduzido = listaStatus.value.find(s => s.id == valor_antigo)?.nome || antigoTraduzido;
            novoTraduzido = listaStatus.value.find(s => s.id == valor_novo)?.nome || novoTraduzido;
        }
        else if (campo === 'prioridade_id') {
            antigoTraduzido = listaPrioridades.value.find(p => p.id == valor_antigo)?.nome || antigoTraduzido;
            novoTraduzido = listaPrioridades.value.find(p => p.id == valor_novo)?.nome || novoTraduzido;
        }
        else if (campo === 'responsavel_acao_id') {
            antigoTraduzido = listaUsuarios.value.find(u => u.id == valor_antigo)?.nome || antigoTraduzido;
            novoTraduzido = listaUsuarios.value.find(u => u.id == valor_novo)?.nome || novoTraduzido;
        }
        }  
        catch (e) {
        // Se as listas não carregaram, falha silenciosamente e usa os IDs (valores padrão)
        console.warn("Falha ao traduzir valores do log, listas podem não estar carregadas.", e);
    }
    return `alterou o campo '${nomeCampoTraduzido}' de '${antigoTraduzido}' para '${novoTraduzido}'`;
}

// --- 6. LIFECYCLE ---
onMounted(() => {
    carregarDadosDoChamado()
})
</script>

<template>
    <div class="detalhe-chamado-container">
    
        <div v-if="isLoading" class="loading">
        Carregando dados do chamado...
        </div>

        <div v-else-if="erro" class="erro">
            <p>{{ erro }}</p>
            <button @click="router.push('/lista-chamados')">Voltar para a Lista</button>
        </div>

        <div v-else-if="chamado" class="conteudo">
<<<<<<< HEAD
    
    <div class="chamado-header">
        <h1>Chamado #{{ chamado.id }}: {{ chamado.contato || 'N/A' }}</h1> 
        <div class="info-bar-edicao">

            <div class="campo-info">
                <label>Empresa:</label>
                <strong>{{ chamado.empresa?.nome || 'N/A' }}</strong>
=======
            
            <div class="chamado-header">
                <h1>Chamado #{{ chamado.id }}: {{ chamado.contato }}</h1>
                <div class="info-bar-edicao">

                <div class="campo-info">
                    <label>Empresa:</label>
                    <strong>{{ chamado.empresa?.nome || 'N/A' }}</strong>
                </div>

                <div class="campo-info">
                    <label for="select-status">Status:</label>
                    <select 
                        id="select-status"
                        v-model="chamado.status_id" 
                        @change="atualizarCampoChamado('status_id', $event.target.value)">
                        <option v-for="s in listaStatus" :key="s.id" :value="s.id">{{ s.nome }}</option>
                    </select>
                </div>

                <div class="campo-info">
                    <label for="select-prioridade">Prioridade:</label>
                    <select 
                        id="select-prioridade"
                        v-model="chamado.prioridade_id" 
                        @change="atualizarCampoChamado('prioridade_id', $event.target.value)">
                        <option v-for="p in listaPrioridades" :key="p.id" :value="p.id">{{ p.nome }}</option>
                    </select>
                </div>

                <div class="campo-info">
                    <label for="select-responsavel">Responsável Ação:</label>
                    <select 
                        id="select-responsavel"
                        v-model="chamado.responsavel_acao_id" 
                        @change="atualizarCampoChamado('responsavel_acao_id', $event.target.value)">
                        <option :value="null">Ninguém</option>
                        <option v-for="u in listaUsuarios" :key="u.id" :value="u.id">{{ u.nome }}</option>
                    </select>
                </div>

>>>>>>> parent of eaddf0f (feat(chamado): melhora layout e responsividade da view de detalhes)
            </div>
            <div class="relato-inicial">
                <strong>Relato Inicial:</strong>
                <p>{{ chamado.relato }}</p>
            </div>
        </div>

            <div class="campo-info">
                <label for="select-status">Status:</label>
                <select 
                    id="select-status"
                    v-model="chamado.status_id" 
                    @change="atualizarCampoChamado('status_id', $event.target.value)">
                    <option v-for="s in listaStatus" :key="s.id" :value="s.id">{{ s.nome }}</option>
                </select>
            </div>

            <div class="campo-info">
                <label>Abertura:</label>
                <strong>{{ formatarData(chamado.datetime_abertura) || 'N/A' }}</strong>
            </div>

            <div class="campo-info">
                <label for="select-prioridade">Prioridade:</label>
                <select 
                    id="select-prioridade"
                    v-model="chamado.prioridade_id" 
                    @change="atualizarCampoChamado('prioridade_id', $event.target.value)">
                    <option v-for="p in listaPrioridades" :key="p.id" :value="p.id">{{ p.nome }}</option>
                </select>
            </div>

            <div class="campo-info">
                <label for="select-atendimento">Responsável Atendimento:</label>
                <select 
                    id="select-atendimento"
                    v-model="chamado.responsavel_atendimento_id" 
                    @change="atualizarCampoChamado('responsavel_atendimento_id', $event.target.value)">
                    <option :value="null">Ninguém</option>
                    <option v-for="u in listaUsuarios" :key="u.id" :value="u.id">{{ u.nome }}</option>
                </select>
            </div>

            <div class="campo-info">
                <label for="select-responsavel">Responsável Ação:</label>
                <select 
                    id="select-responsavel"
                    v-model="chamado.responsavel_acao_id" 
                    @change="atualizarCampoChamado('responsavel_acao_id', $event.target.value)">
                    <option :value="null">Ninguém</option>
                    <option v-for="u in listaUsuarios" :key="u.id" :value="u.id">{{ u.nome }}</option>
                </select>
            </div>

            <div class="campo-info">
                <label for="select-maquina">Tipo de Máquina:</label>
                <select 
                    id="select-maquina"
                    v-model="chamado.tipo_maquina_id" 
                    @change="atualizarCampoChamado('tipo_maquina_id', $event.target.value)">
                    <option :value="null">N/A</option>
                    <option v-for="m in listaMaquinas" :key="m.id" :value="m.id">{{ m.modelo }}</option>
                </select>
            </div>

            <div class="campo-info">
                <label for="select-origem">Origem do Problema:</label>
                <select 
                    id="select-origem"
                    v-model="chamado.origem_id" 
                    @change="atualizarCampoChamado('origem_id', $event.target.value)">
                    <option :value="null">N/A</option>
                    <option v-for="o in listaOrigens" :key="o.id" :value="o.id">{{ o.nome }}</option>
                </select>
            </div>

            <div class="relato-inicial">
                <strong>Relato Inicial:</strong>
                <p>{{ chamado.relato }}</p>
            </div>

        </div>
    </div>
    </div>

        <hr />

        <h2>Histórico do Chamado</h2>
        <div class="timeline">
            <div v-for="item in historicoOrdenado" :key="item.tipo + '-' + item.id" class="timeline-item">

                <div class="timeline-autor">
                    <strong>{{ item.autor }}</strong>
                    <small class="timeline-data">
                    {{ new Date(item.dataHora).toLocaleString('pt-BR') }}

                    <span v-if="item.updated_at" class="editado-info"> (editado)</span>

                    </small>
                </div>
                <div class="timeline-conteudo">
            
                    <div v-if="item.tipo === 'log'">
                        <em>{{ item.conteudo }}</em>
                    </div>

                    <div v-if="item.tipo === 'anexo'">
                        <span>Anexou o arquivo: </span>
                        <a :href="`https://delphisystem-h97d.onrender.com${item.url}`" target="_blank">{{ item.conteudo }}</a>
                    </div>

                    <div v-if="item.tipo === 'comentario'">
                    
                        <div v-if="edicaoComentario.id === item.id" class="comentario-edicao">
                            <textarea v-model="edicaoComentario.comentario" rows="3"></textarea>
                            <div class="botoes-edicao">
                                <button @click="salvarEdicao" class="btn-salvar">Salvar</button>
                                <button @click="cancelarEdicao" class="btn-cancelar">Cancelar</button>
                            </div>
                        </div>
                
                        <div v-else class="comentario-exibicao">
                            <p>{{ item.conteudo }}</p>
                            <div class="botoes-acao">
                                <button @click="iniciarEdicao(item)" class="btn-link">Editar</button>
                                <button @click="deletarComentario(item.id)" class="btn-link btn-link-danger">Deletar</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <hr />

        <div class="novo-comentario-form">
            <h3>Adicionar ao Histórico</h3>
            <textarea v-model="novoComentarioTexto" rows="4" placeholder="Adicionar um novo comentário..."></textarea>
                <div class="botoes-novo-comentario">
                    <button @click="enviarNovoComentario" class="btn-primario">Enviar Comentário</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Um CSS básico para começar. */
.detalhe-chamado-container {
    padding: 20px;
    max-width: 900px;
    margin: auto;
}
/* --- OTIMIZAÇÃO DO CABEÇALHO --- */
.chamado-header {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    margin-bottom: 20px;
}

.chamado-header h1 {
    margin-top: 0;
    margin-bottom: 25px;
    font-size: 2.2em;
    color: #333;
}

/* 1. O contêiner principal vira um GRID */
.info-bar-edicao {
    display: grid;
    grid-template-columns: auto 1fr; 
    gap: 15px 10px;
    align-items: center;
    margin-bottom: 20px;
}

/* 2. Ocupa as 2 colunas para o "Relato Original" */
.relato-inicial {
    grid-column: 1 / -1; 
    margin-top: 10px;
}

/* 3. Estiliza os labels dentro do grid */
.campo-info label {
    font-weight: bold;
    color: #555;
    font-size: 0.95em;
    text-align: right;
    padding-right: 10px;
}

/* 4. Estiliza os inputs e o texto da empresa */
.campo-info select,
.campo-info strong {
    width: 100%;
    max-width: 350px;
    padding: 8px 10px;
    border: 1px solid #ced4da;
    border-radius: 5px;
    font-size: 1rem;
    background-color: #fff;
    box-sizing: border-box;
}

.campo-info strong {
    background-color: #eee;
    border-color: #ddd;
    padding-top: 9px;
    padding-bottom: 9px;
}

.relato-inicial p {
    margin: 5px 0 0 0;
    padding: 10px;
    border-left: 4px solid #007bff;
    background-color: #fdfdfd;
}

.timeline {
    margin-top: 20px;
}

.timeline-item {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 15px;
    padding: 15px;
    border-bottom: 1px solid #eee;
}

.timeline-autor {
    font-size: 0.9em;
}
.timeline-data {
    display: block;
    font-size: 0.8em;
    color: #666;
}

/* --- Estilos por Tipo --- */
.tipo-log .timeline-conteudo {
    font-style: italic;
    color: #555;
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
}

.tipo-anexo .timeline-conteudo {
    background-color: #f0f8ff;
    padding: 10px;
    border-radius: 5px;
}

.tipo-comentario .timeline-conteudo p {
    margin: 0;
    white-space: pre-wrap; /* Mantém as quebras de linha do comentário */
}

/* --- Estilos dos Formulários --- */
.comentario-edicao textarea {
    width: 100%;
    box-sizing: border-box;
}
.botoes-edicao {
    margin-top: 5px;
}

.botoes-acao {
    display: flex;
    gap: 10px;
    font-size: 0.8em;
    margin-top: 5px;
}
.btn-link {
    background: none;
    border: none;
    padding: 0;
    color: #007bff;
    cursor: pointer;
}
.btn-link-danger {
    color: #dc3545;
}

.novo-comentario-form {
    margin-top: 20px;
}
.novo-comentario-form textarea {
    width: 100%;
    padding: 10px;
    box-sizing: border-box; /* Garante que o padding não estoure a largura */
    border: 1px solid #ccc;
    border-radius: 5px;
    font-family: inherit;
}
.botoes-novo-comentario {
    margin-top: 10px;
    text-align: right;
}

/* Botões genéricos */
.btn-primario, .btn-salvar {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
}
.btn-cancelar {
    background-color: #6c757d;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
    margin-left: 5px;
}

/* edição */
.editado-info {
    font-style: italic;
    color: #6c757d; /* Um cinza sutil */
}
</style>
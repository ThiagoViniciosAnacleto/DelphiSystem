<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { format } from 'date-fns'
import apiClient from '../services/api'

// --- Estado Principal ---
const chamado = ref(null)
const logsTimeline = ref([])
const isLoading = ref(true)
const erro = ref(null)
const listaStatus = ref([])
const listaPrioridades = ref([])
const listaUsuarios = ref([])
const listaMaquinas = ref([])
const listaOrigens = ref([])

// --- Estado para Formulários ---
const novoComentarioTexto = ref('')
const novoComentarioPrivado = ref(false)
const edicaoComentario = ref({ id: null, comentario: '', privado: false })
const arquivoAnexo = ref(null)
const isEnviandoAnexo = ref(false)

// --- Roteamento ---
const route = useRoute()
const router = useRouter()
const chamadoId = route.params.id

const formatarData = (dataString) => {
    if (!dataString) return 'N/A'
    try {
        return format(new Date(dataString), 'dd/MM/yyyy HH:mm')
    } catch {
        return String(dataString)
    }
}

// --- 2. FUNÇÕES DE DADOS (API) ---
async function carregarDadosDoChamado() {
    isLoading.value = true
    erro.value = null

    try {
        const [
            resChamado,
            resLogs,
            resListaStatus,
            resListaPrioridades,
            resListaUsuarios,
            resListaMaquinas,
            resListaOrigens
        ] = await Promise.all([
            apiClient.get(`/chamados/${chamadoId}`),
            apiClient.get(`/chamados/${chamadoId}/timeline`),
            apiClient.get('/status_chamado/'),
            apiClient.get('/prioridades/'),
            apiClient.get('/usuarios/'),
            apiClient.get('/maquinas/'),
            apiClient.get('/origens_problema/')
        ])

        chamado.value = resChamado
        logsTimeline.value = resLogs
        listaStatus.value = resListaStatus
        listaPrioridades.value = resListaPrioridades
        listaUsuarios.value = resListaUsuarios
        listaMaquinas.value = resListaMaquinas
        listaOrigens.value = resListaOrigens

    } catch (err) {
        if (err.status === 404) {
            erro.value = "Chamado não encontrado."
        } else if (err.status === 403) {
            erro.value = "Você não tem permissão para visualizar este chamado."
        } else {
            erro.value = "Falha ao carregar o histórico do chamado: " + err.message
        }
    } finally {
        isLoading.value = false
    }
}


// --- 3. COMPUTED: O HISTÓRICO MESCLADO ---
const historicoOrdenado = computed(() => {
    if (!chamado.value) return []

    // Mapeamento dos comentários
    const comentarios = (Array.isArray(chamado.value.interacoes) ? chamado.value.interacoes : []).map(item => ({
        tipo: 'comentario',
        dataHora: item.data_interacao,
        autor: item.usuario ? item.usuario.nome : 'Usuário Desconhecido',
        conteudo: item.comentario,
        privado: item.privado,
        id: item.id,
        objetoOriginal: item,
        updated_at: item.updated_at
    }))

    // Mapeamento dos logs
    const logs = (Array.isArray(logsTimeline.value) ? logsTimeline.value : []).map(item => ({
        tipo: 'log',
        dataHora: item.data_hora,
        autor: item.usuario ? item.usuario.nome : 'Sistema',
        conteudo: formatarLogConteudo(item),
        id: item.id,
        objetoOriginal: item
    }))

    // Mapeamento dos anexos
    const arquivos = (Array.isArray(chamado.value.anexos) ? chamado.value.anexos : []).map(item => ({
        tipo: 'anexo',
        dataHora: item.data_upload,
        autor: item.usuario ? item.usuario.nome : 'Usuário Desconhecido',
        conteudo: item.nome_arquivo_original,
        url: item.url ? (item.url.startsWith('http') ? item.url : `${baseURL}${item.url}`) : '',
        id: item.id
    }))

    const timeline = [...comentarios, ...logs, ...arquivos]
    return timeline.sort((a, b) => new Date(a.dataHora) - new Date(b.dataHora))
})


// --- 4. FUNÇÕES DE CRUD (AÇÕES) ---

async function enviarNovoComentario() {
    if (!novoComentarioTexto.value.trim()) return

    try {
        const resposta = await apiClient.post(`/chamados/${chamadoId}/interacoes/`, {
            comentario: novoComentarioTexto.value,
            privado: novoComentarioPrivado.value
        })

        if (!chamado.value.interacoes) {
            chamado.value.interacoes = []
        }
        chamado.value.interacoes.push(resposta)
        novoComentarioTexto.value = ''
        novoComentarioPrivado.value = false

    } catch (err) {
        alert("Falha ao salvar comentário: " + (err.message || 'Erro de comunicação'))
    }
}

function iniciarEdicao(comentario) {
    edicaoComentario.value.id = comentario.id
    edicaoComentario.value.comentario = comentario.conteudo
    edicaoComentario.value.privado = !!comentario.privado
}

function cancelarEdicao() {
    edicaoComentario.value.id = null
    edicaoComentario.value.comentario = ''
    edicaoComentario.value.privado = false
}

async function atualizarCampoChamado(campo, valor) {
    const payload = {
        [campo]: valor === '' ? null : valor
    }

    try {
        const chamadoAtualizado = await apiClient.put(`/chamados/${chamadoId}`, payload)
        chamado.value = chamadoAtualizado

        // Atualiza timeline de logs
        logsTimeline.value = await apiClient.get(`/chamados/${chamadoId}/timeline`)

    } catch (err) {
        alert(`Falha ao atualizar o chamado: ${err.message}`)
        carregarDadosDoChamado()
    }
}

async function salvarEdicao() {
    if (!edicaoComentario.value.id) return

    try {
        const resposta = await apiClient.put(`/interacoes/${edicaoComentario.value.id}`, {
            comentario: edicaoComentario.value.comentario,
            privado: edicaoComentario.value.privado
        })

        const index = chamado.value.interacoes.findIndex(c => c.id === edicaoComentario.value.id)
        if (index !== -1) {
            chamado.value.interacoes[index] = resposta
        }

        cancelarEdicao()

    } catch (err) {
        alert("Falha ao salvar edição: " + (err.message || 'Erro de comunicação'))
    }
}

async function deletarComentario(comentarioId) {
    if (!confirm("Tem certeza que deseja deletar este comentário?")) return

    try {
        await apiClient.delete(`/interacoes/${comentarioId}`)
        chamado.value.interacoes = chamado.value.interacoes.filter(c => c.id !== comentarioId)
    } catch (err) {
        alert("Falha ao deletar comentário: " + (err.message || 'Erro de comunicação'))
    }
}

function onArquivoSelecionado(event) {
    const files = event.target.files
    if (files && files.length > 0) {
        arquivoAnexo.value = files[0]
    } else {
        arquivoAnexo.value = null
    }
}

async function enviarAnexo() {
    if (!arquivoAnexo.value) {
        alert("Selecione um arquivo para enviar.")
        return
    }

    isEnviandoAnexo.value = true
    try {
        const formData = new FormData()
        formData.append('file', arquivoAnexo.value)

        const anexoCriado = await apiClient.upload(`/chamados/${chamadoId}/anexos/`, formData)
        if (!chamado.value.anexos) {
            chamado.value.anexos = []
        }
        chamado.value.anexos.push(anexoCriado)
        arquivoAnexo.value = null

        const inputElem = document.getElementById('input-file-anexo')
        if (inputElem) inputElem.value = ''

        alert('Anexo enviado com sucesso!')
    } catch (err) {
        alert("Erro ao enviar anexo: " + (err.message || 'Erro de upload'))
    } finally {
        isEnviandoAnexo.value = false
    }
}

async function baixarAnexo(item) {
    try {
        await apiClient.download(item.url || `/anexos/${item.id}`, item.conteudo || 'anexo')
    } catch (err) {
        alert(err.message || 'Falha ao baixar anexo')
    }
}


function formatarLogConteudo(logItem) {
    const { acao, campo, valor_antigo, valor_novo } = logItem

    if (acao !== 'atualizacao') {
        return logItem.conteudo || acao
    }

    const nomesCampos = {
        status_id: 'Status',
        prioridade_id: 'Prioridade',
        responsavel_atendimento_id: 'Responsável (Atendimento)',
        responsavel_acao_id: 'Responsável (Ação)',
        tipo_maquina_id: 'Tipo de Máquina',
        origem_id: 'Origem do Problema',
        contato: 'Contato',
        porta_ssh: 'Porta SSH',
        relato: 'Relato',
        acao_realizada: 'Ação Realizada'
    }
    const nomeCampoTraduzido = nomesCampos[campo] || campo

    let antigoTraduzido = valor_antigo || 'vazio'
    let novoTraduzido = valor_novo || 'vazio'

    try {
        if (campo === 'status_id') {
            antigoTraduzido = listaStatus.value.find(s => String(s.id) === String(valor_antigo))?.nome || antigoTraduzido
            novoTraduzido = listaStatus.value.find(s => String(s.id) === String(valor_novo))?.nome || novoTraduzido
        } else if (campo === 'prioridade_id') {
            antigoTraduzido = listaPrioridades.value.find(p => String(p.id) === String(valor_antigo))?.nome || antigoTraduzido
            novoTraduzido = listaPrioridades.value.find(p => String(p.id) === String(valor_novo))?.nome || novoTraduzido
        } else if (campo === 'responsavel_acao_id' || campo === 'responsavel_atendimento_id') {
            antigoTraduzido = listaUsuarios.value.find(u => String(u.id) === String(valor_antigo))?.nome || antigoTraduzido
            novoTraduzido = listaUsuarios.value.find(u => String(u.id) === String(valor_novo))?.nome || novoTraduzido
        } else if (campo === 'tipo_maquina_id') {
            antigoTraduzido = listaMaquinas.value.find(m => String(m.id) === String(valor_antigo))?.modelo || antigoTraduzido
            novoTraduzido = listaMaquinas.value.find(m => String(m.id) === String(valor_novo))?.modelo || novoTraduzido
        } else if (campo === 'origem_id') {
            antigoTraduzido = listaOrigens.value.find(o => String(o.id) === String(valor_antigo))?.nome || antigoTraduzido
            novoTraduzido = listaOrigens.value.find(o => String(o.id) === String(valor_novo))?.nome || novoTraduzido
        }
    } catch (e) {
        console.warn("Falha ao traduzir valores do log:", e)
    }

    return `alterou o campo '${nomeCampoTraduzido}' de '${antigoTraduzido}' para '${novoTraduzido}'`
}

onMounted(() => {
    carregarDadosDoChamado()
})
</script>

<template>
    <div class="detalhe-chamado-container">

        <div v-if="isLoading" class="loading" aria-live="polite">
            Carregando dados do chamado...
        </div>

        <div v-else-if="erro" class="erro" aria-live="polite">
            <p>{{ erro }}</p>
            <button @click="router.push('/lista-chamados')" class="btn-primario">Voltar para a Lista</button>
        </div>

        <div v-else-if="chamado" class="conteudo">
            <div class="chamado-header">
                <h1>Chamado #{{ chamado.id }}: {{ chamado.contato || 'N/A' }}</h1>

                <div class="info-bar-edicao">
                    <div class="campo-info">
                        <label>Empresa:</label>
                        <strong>{{ chamado.empresa?.nome || 'N/A' }}</strong>
                    </div>

                    <div class="campo-info">
                        <label>Data de Abertura:</label>
                        <strong>{{ formatarData(chamado.datetime_abertura) }}</strong>
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
                            <option :value="null">Selecione</option>
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

                    <div class="campo-info">
                        <label>Porta SSH:</label>
                        <strong>{{ chamado.porta_ssh || 'N/A' }}</strong>
                    </div>

                    <div class="relato-inicial">
                        <strong>Relato Inicial:</strong>
                        <p>{{ chamado.relato }}</p>
                    </div>

                    <div v-if="chamado.acao_realizada" class="relato-inicial">
                        <strong>Ação Realizada:</strong>
                        <p>{{ chamado.acao_realizada }}</p>
                    </div>
                </div>
            </div>

            <hr />

            <!-- Seção de Anexos -->
            <div class="secao-anexos">
                <h2>Anexos</h2>
                <div class="novo-anexo-form">
                    <label for="input-file-anexo" class="form-label">Adicionar Anexo:</label>
                    <div class="d-flex gap-2 align-items-center">
                        <input id="input-file-anexo" type="file" @change="onArquivoSelecionado" class="form-control" />
                        <button @click="enviarAnexo" :disabled="!arquivoAnexo || isEnviandoAnexo" class="btn-primario">
                            {{ isEnviandoAnexo ? 'Enviando...' : 'Enviar Anexo' }}
                        </button>
                    </div>
                </div>
            </div>

            <hr />

            <h2>Histórico do Chamado</h2>
            <div class="timeline">
                <div v-for="item in historicoOrdenado" :key="item.tipo + '-' + item.id" :class="['timeline-item', 'tipo-' + item.tipo]">
                    <div class="timeline-autor">
                        <strong>{{ item.autor }}</strong>
                        <small class="timeline-data">
                            {{ formatarData(item.dataHora) }}
                            <span v-if="item.updated_at" class="editado-info"> (editado)</span>
                            <span v-if="item.privado" class="badge-privado"> [Interno]</span>
                        </small>
                    </div>

                    <div class="timeline-conteudo">
                        <div v-if="item.tipo === 'log'">
                            <em>{{ item.conteudo }}</em>
                        </div>

                        <div v-if="item.tipo === 'anexo'">
                            <span>📎 Arquivo anexado: </span>
                            <button type="button" class="btn-link btn-download-anexo" @click="baixarAnexo(item)">{{ item.conteudo }} (baixar)</button>
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
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <label class="d-flex align-items-center gap-1">
                        <input type="checkbox" v-model="novoComentarioPrivado" />
                        Comentário interno (privado)
                    </label>
                    <div class="botoes-novo-comentario">
                        <button @click="enviarNovoComentario" class="btn-primario">Enviar Comentário</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.detalhe-chamado-container {
    padding: 20px;
    max-width: 950px;
    margin: auto;
}
.chamado-header {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    margin-bottom: 20px;
}
.chamado-header h1 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 1.8em;
    color: #333;
}
.info-bar-edicao {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 15px 20px;
    align-items: center;
    margin-bottom: 10px;
}
.campo-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.campo-info label {
    font-weight: bold;
    color: #555;
    font-size: 0.9em;
}
.campo-info select,
.campo-info strong {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid #ced4da;
    border-radius: 5px;
    font-size: 0.95rem;
    background-color: #fff;
    box-sizing: border-box;
}
.campo-info strong {
    background-color: #f0f0f0;
    border-color: #ddd;
    color: #333;
}
.relato-inicial {
    grid-column: 1 / -1;
    margin-top: 10px;
}
.relato-inicial p {
    margin: 5px 0 0 0;
    padding: 10px;
    border-left: 4px solid #007bff;
    background-color: #fdfdfd;
    white-space: pre-wrap;
}
.secao-anexos {
    margin: 20px 0;
}
.novo-anexo-form {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    border: 1px solid #e9ecef;
}
.timeline {
    margin-top: 20px;
}
.timeline-item {
    display: grid;
    grid-template-columns: 180px 1fr;
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
.badge-privado {
    color: #d9534f;
    font-weight: bold;
}
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
    white-space: pre-wrap;
}
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
    box-sizing: border-box;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-family: inherit;
}
.botoes-novo-comentario {
    text-align: right;
}
.btn-primario, .btn-salvar {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 14px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
}
.btn-primario:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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
.editado-info {
    font-style: italic;
    color: #6c757d;
}
.loading, .erro {
    padding: 20px;
    text-align: center;
}
.erro {
    color: #dc3545;
}
</style>

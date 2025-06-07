<template>
    <div class="lista-chamados">
        <h2>Lista de Chamados</h2>

        <div class="filtros">
            <input v-model="filtros.contato" placeholder="Filtrar por Contato" />
            
            <select v-model="filtros.empresa_id">
                <option :value="null">Filtrar por Empresa</option>
                <option v-for="e in empresas" :value="e.id" :key="e.id">{{ e.nome }}</option>
            </select>

            <select v-model="filtros.status_id">
                <option :value="null">Filtrar por Status</option>
                <option v-for="s in status" :value="s.id" :key="s.id">{{ s.nome }}</option>
            </select>

            <select v-model="filtros.prioridade_id">
                <option :value="null">Filtrar por Prioridade</option>
                <option v-for="p in prioridades" :value="p.id" :key="p.id">{{ p.nome }}</option>
            </select>
            
            <select v-model="filtros.responsavel_id">
                <option :value="null">Filtrar por Responsável</option>
                <option v-for="u in usuarios" :value="u.id" :key="u.id">{{ u.nome }}</option>
            </select>

            <button @click="aplicarFiltros">Aplicar Filtros</button>
            <button @click="limparFiltros">Limpar Filtros</button>
        </div>

        <div v-if="chamados.length" class="tabela-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Data Abertura</th>
                        <th>Contato</th>
                        <th>Empresa</th>
                        <th>Relato</th>
                        <th>Status</th>
                        <th>Prioridade</th>
                        <th>Responsável</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="chamado in chamados" :key="chamado.id">
                        <td>{{ chamado.id }}</td>
                        <td>{{ formatarData(chamado.datetime_abertura) }}</td>
                        <td>{{ chamado.contato }}</td>
                        <td>{{ chamado.empresa ? chamado.empresa.nome : 'N/A' }}</td>
                        <td>{{ truncateText(chamado.relato, 50) }}</td>
                        <td>{{ chamado.status ? chamado.status.nome : 'N/A' }}</td>
                        <td>{{ chamado.prioridade ? chamado.prioridade.nome : 'N/A' }}</td>
                        <td>{{ chamado.responsavel_atendimento ? chamado.responsavel_atendimento.nome : 'N/A' }}</td>
                        <td>
                        <button @click="verDetalhes(chamado.id)" class="btn-detalhes">Detalhes</button>
                        <button @click="editarChamado(chamado.id)" class="btn-editar">Editar</button>
                        <button @click="deletarChamado(chamado.id)" class="btn-deletar">Excluir</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div v-else class="sem-chamados">
            <p>Nenhum chamado encontrado com os filtros aplicados.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { format } from 'date-fns';

const router = useRouter();

const chamados = ref([]);
const empresas = ref([]);
const status = ref([]);
const prioridades = ref([]);
const usuarios = ref([]);

const filtros = ref({
    contato: '',
    empresa_id: null,
    status_id: null,
    prioridade_id: null,
    responsavel_id: null,
    order_by: 'datetime_abertura',
    desc: true,
});

// --- Configurações da API ---
const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '');
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`,
};

// --- Funções Auxiliares de API ---
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
        throw error; // Re-lança para ser capturado por quem chamou
    }
};

// --- Funções de Carregamento de Dados Iniciais ---
const carregarDadosBase = async () => {
    try {
        // Carrega dados para todos os selects de filtro
        empresas.value = await fetchData('/empresas/');
        status.value = await fetchData('/status_chamado/');
        prioridades.value = await fetchData('/prioridades/');
        usuarios.value = await fetchData('/usuarios/');
    } catch (error) {
        console.error("Falha ao carregar dados base para filtros.");
    }
};

const carregarChamados = async () => {
    try {
        const params = new URLSearchParams();

        if (filtros.value.contato) params.append('contato', filtros.value.contato);
        if (filtros.value.empresa_id) params.append('empresa_id', filtros.value.empresa_id);
        if (filtros.value.status_id) params.append('status_id', filtros.value.status_id);
        if (filtros.value.prioridade_id) params.append('prioridade_id', filtros.value.prioridade_id);
        if (filtros.value.responsavel_id) params.append('responsavel_id', filtros.value.responsavel_id);

        params.append('order_by', filtros.value.order_by);
        params.append('desc', filtros.value.desc); 

        const url = `${baseURL}/chamados/?${params.toString()}`;

        const chamadosData = await fetchData(url.replace(baseURL, ''));
        chamados.value = chamadosData;
        console.log("Chamados carregados:", chamados.value);
    } catch (error) {
        console.error("Falha ao carregar chamados.");
        chamados.value = [];
    }
};

// --- Funções de Controle de Filtros ---
const aplicarFiltros = () => {
    carregarChamados();
};

const limparFiltros = () => {
    // Reseta todos os filtros para seus valores padrão
    filtros.value = {
        contato: '',
        empresa_id: null,
        status_id: null,
        prioridade_id: null,
        responsavel_id: null,
        order_by: 'datetime_abertura', // Volta para o padrão de ordenação
        desc: true, // Volta para o padrão de direção
    };
    carregarChamados(); // Recarrega chamados sem filtros
};

// --- Funções de Ação na Tabela ---
const verDetalhes = (id) => {
    // Exemplo de navegação: router.push(`/chamados/${id}`);
    alert(`Ver detalhes do chamado ${id}`); // Placeholder
};

const editarChamado = (id) => {
    // Exemplo de navegação: router.push(`/chamados/${id}/editar`);
    alert(`Editar chamado ${id}`); // Placeholder
};

const deletarChamado = async (id) => {
    if (confirm(`Tem certeza que deseja desativar o chamado ID ${id}?`)) {
        try {
            const res = await fetch(`${baseURL}/chamados/${id}`, {
                method: 'DELETE',
                headers,
            });

            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || `Erro HTTP ${res.status} ao desativar chamado`);
            }

            alert('Chamado desativado com sucesso!');
            carregarChamados(); // Recarrega a lista após a desativação
        } catch (error) {
            console.error('Erro ao desativar chamado:', error);
            alert(`Erro ao desativar chamado: ${error.message}`);
        }
    }
};

// --- Funções Utilitárias de Formatação ---
const formatarData = (dataString) => {
    return dataString ? format(new Date(dataString), 'dd/MM/yyyy HH:mm') : 'N/A';
};

const truncateText = (text, maxLength) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

// --- Ciclo de Vida do Componente ---
onMounted(async () => {
    await carregarDadosBase(); // Carrega os dados para os selects de filtro primeiro
    await carregarChamados(); // Em seguida, carrega a lista de chamados
});
</script>

<style scoped>
.lista-chamados {
    max-width: 1200px;
    margin: 40px auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    font-family: 'Segoe UI', sans-serif;
}

h2 {
    text-align: center;
    color: #1a1a1a;
    margin-bottom: 25px;
}

.filtros {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 30px;
    padding: 15px;
    background-color: #e9ecef;
    border-radius: 8px;
}

.filtros input,
.filtros select {
    flex: 1;
    min-width: 180px;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 5px;
    font-size: 15px;
}

.filtros button {
    padding: 10px 20px;
    font-size: 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s;
    background-color: #007bff;
    color: white;
}

.filtros button:hover {
    background-color: #0056b3;
}

.filtros button:last-child {
    background-color: #6c757d;
}

.filtros button:last-child:hover {
    background-color: #5a6268;
}

.tabela-container {
    overflow-x: auto; /* Permite scroll horizontal em telas menores */
    border: 1px solid #dee2e6;
    border-radius: 8px;
}

table {
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff;
}

thead th {
    background-color: #007bff;
    color: white;
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
    white-space: nowrap; /* Evita que o texto quebre */
}

tbody td {
    padding: 10px 15px;
    border-bottom: 1px solid #dee2e6;
    vertical-align: top;
    white-space: nowrap;
}

tbody tr:hover {
    background-color: #f2f2f2;
}

.sem-chamados {
    text-align: center;
    padding: 30px;
    color: #6c757d;
    font-size: 1.1em;
    background-color: #e9ecef;
    border-radius: 8px;
    margin-top: 20px;
}

.btn-detalhes, .btn-editar, .btn-deletar {
    padding: 6px 10px;
    font-size: 13px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-right: 5px;
    transition: background-color 0.2s;
}

.btn-detalhes {
    background-color: #17a2b8;
    color: white;
}
.btn-detalhes:hover { background-color: #138496; }

.btn-editar {
    background-color: #ffc107;
    color: #333;
}
.btn-editar:hover { background-color: #e0a800; }

.btn-deletar {
    background-color: #dc3545;
    color: white;
}
.btn-deletar:hover { background-color: #c82333; }
</style>
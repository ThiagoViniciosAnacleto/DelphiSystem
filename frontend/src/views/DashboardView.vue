<template>
  <div class="dashboard-container">
    <h2>📊 Painel de Controle (Dashboard)</h2>

    <div v-if="isLoading" class="loading" aria-live="polite">Carregando métricas...</div>

    <div v-else class="dashboard-content">
      <!-- Cards de Status Básicos -->
      <div class="cards-grid">
        <div class="metric-card" v-for="(qtd, statusNome) in statusCounts" :key="statusNome">
          <span class="metric-title">{{ statusNome }}</span>
          <span class="metric-value">{{ qtd }}</span>
        </div>
      </div>

      <!-- Seção Avançada -->
      <div class="charts-grid" v-if="avancado">
        <div class="panel-card">
          <h3>Chamados por Empresa</h3>
          <ul v-if="avancado.por_empresa && avancado.por_empresa.length">
            <li v-for="item in avancado.por_empresa" :key="item.empresa">
              <span>{{ item.empresa }}</span>
              <strong>{{ item.quantidade }}</strong>
            </li>
          </ul>
          <p v-else class="empty-text">Nenhum dado registrado.</p>
        </div>

        <div class="panel-card">
          <h3>Chamados por Técnico</h3>
          <ul v-if="avancado.por_tecnico && avancado.por_tecnico.length">
            <li v-for="item in avancado.por_tecnico" :key="item.tecnico">
              <span>{{ item.tecnico }}</span>
              <strong>{{ item.quantidade }}</strong>
            </li>
          </ul>
          <p v-else class="empty-text">Nenhum dado registrado.</p>
        </div>

        <div class="panel-card full-width">
          <h3>Chamados nos Últimos 7 Dias</h3>
          <div class="dias-grid" v-if="avancado.ultimos_7_dias && avancado.ultimos_7_dias.length">
            <div class="dia-item" v-for="dia in avancado.ultimos_7_dias" :key="dia.data">
              <span class="dia-label">{{ dia.data }}</span>
              <span class="dia-badge">{{ dia.quantidade }} chamado(s)</span>
            </div>
          </div>
          <p v-else class="empty-text">Sem atividade recente.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../services/api'

const isLoading = ref(true)
const statusCounts = ref({})
const avancado = ref(null)

const carregarDashboard = async () => {
  isLoading.value = true
  try {
    const [resBasico, resAvancado] = await Promise.all([
      apiClient.get('/dashboard/basico'),
      apiClient.get('/dashboard/avancado')
    ])

    statusCounts.value = resBasico || {}
    avancado.value = resAvancado || null
  } catch (err) {
    // Trata erro graciosamente
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  carregarDashboard()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1000px;
  margin: auto;
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}
.metric-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.metric-title {
  font-size: 0.9em;
  color: #666;
  text-transform: uppercase;
}
.metric-value {
  font-size: 2em;
  font-weight: bold;
  color: #007bff;
}
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.panel-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.panel-card h3 {
  margin-top: 0;
  font-size: 1.1em;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}
.panel-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.panel-card li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}
.full-width {
  grid-column: 1 / -1;
}
.dias-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.dia-item {
  background: #f8f9fa;
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  text-align: center;
}
.dia-label {
  display: block;
  font-size: 0.85em;
  color: #555;
}
.dia-badge {
  font-weight: bold;
  color: #28a745;
}
.empty-text {
  color: #888;
  font-style: italic;
}
.loading {
  text-align: center;
  padding: 30px;
  color: #666;
}
</style>

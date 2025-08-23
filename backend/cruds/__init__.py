from .chamado import (
    criar_chamado,
    listar_chamados,
    atualizar_chamado,
    deletar_chamado,
)

from .chamado_recorrente import (
    criar_chamado_recorrente,
    listar_chamados_recorrentes,
    atualizar_chamado_recorrente,
    deletar_chamado_recorrente,
)

from .empresa import (
    criar_empresa,
    listar_empresas,
    atualizar_empresa,
    deletar_empresa,
)

from .frequencia import (
    criar_frequencia,
    listar_frequencias,
    atualizar_frequencia,
    deletar_frequencia,
)

from .log_acao import (
    criar_log_acao,
    listar_logs,
    buscar_log_por_id,
    deletar_log,
)

from .maquina import (
    criar_maquina,
    listar_maquinas,
    buscar_maquina_por_id,
    atualizar_maquina,
    deletar_maquina,
)

from .origem_problema import (
    criar_origem_problema,
    listar_origens_problema,
    buscar_origem_problema_por_id,
    atualizar_origem_problema,
    deletar_origem_problema,
)

from .prioridade import (
    criar_prioridade,
    listar_prioridades,
    buscar_prioridade_por_id,
    atualizar_prioridade,
    deletar_prioridade,
)

from .role import (
    criar_role,
    listar_roles,
    buscar_role_por_id,
    atualizar_role,
    deletar_role,
)

from .status import (
    criar_status,
    listar_status,
    buscar_status_por_id,
    atualizar_status,
    deletar_status,
)

from .usuario import (
    criar_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    atualizar_usuario,
    deletar_usuario,
    get_usuario_por_email,
)

from .tag import (
    criar_tag, 
    listar_tags, 
    buscar_tag_por_id, 
    buscar_tag_por_nome, 
    deletar_tag,
)

from .interacao import (
    criar_interacao,
    listar_interacoes_por_chamado,
    buscar_interacao_por_id,
    atualizar_interacao,
    deletar_interacao,
)

from .anexo import (
    criar_anexo,
    listar_anexos_por_chamado,
    buscar_anexo_por_id,
    deletar_anexo,
)

__all__ = [
    # Chamado
    "criar_chamado",
    "listar_chamados",
    "buscar_chamado_por_id",
    "atualizar_chamado",
    "deletar_chamado",
    # ChamadoRecorrente
    "criar_chamado_recorrente",
    "listar_chamados_recorrentes",
    "buscar_chamado_recorrente_por_id",
    "atualizar_chamado_recorrente",
    "deletar_chamado_recorrente",
    # Empresa
    "criar_empresa",
    "listar_empresas",
    "buscar_empresa_por_id",
    "atualizar_empresa",
    "deletar_empresa",
    # Frequencia
    "criar_frequencia",
    "listar_frequencias",
    "buscar_frequencia_por_id",
    "atualizar_frequencia",
    "deletar_frequencia",
    # LogAcao
    "criar_log_acao",
    "listar_logs",
    "buscar_log_por_id",
    "deletar_log",
    # Maquina
    "criar_maquina",
    "listar_maquinas",
    "buscar_maquina_por_id",
    "atualizar_maquina",
    "deletar_maquina",
    # OrigemProblema
    "criar_origem_problema",
    "listar_origens_problema",
    "buscar_origem_problema_por_id",
    "atualizar_origem_problema",
    "deletar_origem_problema",
    # Prioridade
    "criar_prioridade",
    "listar_prioridades",
    "buscar_prioridade_por_id",
    "atualizar_prioridade",
    "deletar_prioridade",
    # Role
    "criar_role",
    "listar_roles",
    "buscar_role_por_id",
    "atualizar_role",
    "deletar_role",
    # Status
    "criar_status",
    "listar_status",
    "buscar_status_por_id",
    "atualizar_status",
    "deletar_status",
    # Usuario
    "criar_usuario",
    "listar_usuarios",
    "buscar_usuario_por_id",
    "atualizar_usuario",
    "deletar_usuario",
    "get_usuario_por_email",
    # Tag
    "criar_tag", 
    "listar_tags", 
    "buscar_tag_por_id", 
    "buscar_tag_por_nome", 
    "deletar_tag",
    # Interação
    "criar_interacao",
    "listar_interacoes_por_chamado",
    "buscar_interacao_por_id",
    "atualizar_interacao",
    "deletar_interacao",
    # Anexo
    "criar_anexo",
    "listar_anexos_por_chamado",
    "buscar_anexo_por_id",
    "deletar_anexo",
]

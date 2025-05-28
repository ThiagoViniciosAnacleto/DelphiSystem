from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    TIMESTAMP,
)
from datetime import datetime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class SoftDeleteMixin:
    ativo = Column(Boolean, nullable=False, default=True, index=True)

class Role(Base, SoftDeleteMixin):
    """Tabela de cargos/perfis de usuários (ex: admin, técnico, comum)."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)

    # Soft delete
    ativo = Column(Boolean, nullable=False, default=True, index=True)

    nome = Column(String(100), unique=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="role")


class Prioridade(Base):
    """Tabela de prioridades possíveis para chamados (ex: baixa, média, alta)."""
    __tablename__ = "prioridades"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)

    chamados = relationship("Chamado", back_populates="prioridade_obj")


class Status(Base):
    """Tabela de status possíveis para chamados (ex: aberto, em andamento, fechado)."""
    __tablename__ = "status"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)

    chamados = relationship("Chamado", back_populates="status_obj")


class Frequencia(Base):
    """Tabela de frequências para chamados recorrentes (ex: diária, semanal, mensal)."""
    __tablename__ = "frequencias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)

    chamados_recorrentes = relationship("ChamadoRecorrente", back_populates="frequencia")


class Usuario(Base, SoftDeleteMixin):
    """Tabela de usuários do sistema."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    # Soft delete
    ativo = Column(Boolean, nullable=False, default=True, index=True)

    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    role = relationship("Role", back_populates="usuarios")

    created_at = Column(
        TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
        onupdate="CURRENT_TIMESTAMP",
    )

    chamados_atendimento = relationship(
        "Chamado",
        back_populates="responsavel_atendimento",
        foreign_keys="Chamado.responsavel_atendimento_id",
    )
    chamados_acao = relationship(
        "Chamado",
        back_populates="responsavel_acao",
        foreign_keys="Chamado.responsavel_acao_id",
    )
    log_acoes = relationship("LogAcao", back_populates="usuario")


class Empresa(Base):
    """Tabela das empresas/empregadores/clientes."""
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), unique=True, index=True, nullable=False)

    created_at = Column(
        TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP"
    )

    chamados = relationship("Chamado", back_populates="empresa")
    chamados_recorrentes = relationship("ChamadoRecorrente", back_populates="empresa")


class Maquina(Base):
    """Tabela de modelos ou tipos de máquinas."""
    __tablename__ = "maquinas"

    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String(150), unique=True, nullable=False)

    chamados = relationship("Chamado", back_populates="tipo_maquina")
    chamados_recorrentes = relationship("ChamadoRecorrente", back_populates="tipo_maquina")


class OrigemProblema(Base):
    """Tabela de origens de problemas relatados."""
    __tablename__ = "origens_problema"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), unique=True, nullable=False)

    chamados = relationship("Chamado", back_populates="origem")
    chamados_recorrentes = relationship("ChamadoRecorrente", back_populates="origem")


class Chamado(Base, SoftDeleteMixin):
    """Tabela principal de chamados técnicos."""
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, index=True)

    # Soft delete
    ativo = Column(Boolean, nullable=False, default=True, index=True)

    responsavel_atendimento_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    responsavel_acao_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True, index=True)
    tipo_maquina_id = Column(Integer, ForeignKey("maquinas.id"), nullable=True, index=True)
    origem_id = Column(Integer, ForeignKey("origens_problema.id"), nullable=True, index=True)

    datetime_abertura = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow, index=True)

    cliente = Column(String(150), nullable=True, index=True)
    porta_ssh = Column(String(100), nullable=True)

    relato = Column(Text, nullable=True)

    prioridade_id = Column(Integer, ForeignKey("prioridades.id"), nullable=True, index=True)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=True, index=True)

    descricao_acao = Column(Text, nullable=True)

    prioridade_obj = relationship("Prioridade", back_populates="chamados")
    status_obj = relationship("Status", back_populates="chamados")

    responsavel_atendimento = relationship(
        "Usuario",
        foreign_keys=[responsavel_atendimento_id],
        back_populates="chamados_atendimento",
    )
    responsavel_acao = relationship(
        "Usuario", foreign_keys=[responsavel_acao_id], back_populates="chamados_acao"
    )
    empresa = relationship("Empresa", back_populates="chamados")
    tipo_maquina = relationship("Maquina", back_populates="chamados")
    origem = relationship("OrigemProblema", back_populates="chamados")

    logs = relationship("LogAcao", back_populates="chamado")


class ChamadoRecorrente(Base):
    """Tabela de chamados recorrentes, gerenciando frequências e próximas execuções."""
    __tablename__ = "chamados_recorrentes"

    id = Column(Integer, primary_key=True, index=True)

    cliente = Column(String(150), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    porta_ssh = Column(String(100), nullable=True)
    tipo_maquina_id = Column(Integer, ForeignKey("maquinas.id"), nullable=True)
    relato = Column(Text, nullable=False)

    prioridade_id = Column(Integer, ForeignKey("prioridades.id"), nullable=True)
    prioridade = relationship("Prioridade")

    origem_id = Column(Integer, ForeignKey("origens_problema.id"), nullable=True)
    responsavel_atendimento_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    responsavel_acao_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    descricao_acao = Column(Text, nullable=True)

    frequencia_id = Column(Integer, ForeignKey("frequencias.id"), nullable=False)
    frequencia = relationship("Frequencia", back_populates="chamados_recorrentes")

    proxima_execucao = Column(DateTime(timezone=True), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    empresa = relationship("Empresa", back_populates="chamados_recorrentes")
    tipo_maquina = relationship("Maquina", back_populates="chamados_recorrentes")
    origem = relationship("OrigemProblema", back_populates="chamados_recorrentes")


class LogAcao(Base, SoftDeleteMixin):
    """Tabela para armazenar logs das ações realizadas por usuários em chamados."""
    __tablename__ = "log_acoes"

    # Soft delete
    ativo = Column(Boolean, nullable=False, default=True, index=True)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    chamado_id = Column(Integer, ForeignKey("chamados.id"), nullable=True)

    acao = Column(String, nullable=False)
    data_hora = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")

    tipo = Column(String, nullable=True)
    campo = Column(String, nullable=True)
    valor_antigo = Column(Text, nullable=True)
    valor_novo = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="log_acoes")
    chamado = relationship("Chamado", back_populates="logs")
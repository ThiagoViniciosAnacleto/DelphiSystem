from sqlalchemy.sql import func
from sqlalchemy import (
    Table,
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

chamados_tags = Table('chamados_tags', Base.metadata,
    Column('chamado_id', Integer, ForeignKey('chamados.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class SoftDeleteMixin:
    ativo = Column(Boolean, nullable=False, default=True, index=True)

class Role(Base, SoftDeleteMixin):
    """Tabela de cargos/perfis de usuários (ex: admin, técnico, comum)."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(100), unique=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="role")


class Prioridade(Base):
    """Tabela de prioridades possíveis para chamados (ex: baixa, média, alta)."""
    __tablename__ = "prioridades"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)

    chamados = relationship("Chamado", back_populates="prioridade")


class Status(Base):
    """Tabela de status possíveis para chamados (ex: aberto, em andamento, fechado)."""
    __tablename__ = "status"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)

    chamados = relationship("Chamado", back_populates="status")


class Frequencia(Base):
    """Tabela de frequências para chamados recorrentes (ex: diária, semanal, mensal)."""
    __tablename__ = "frequencias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)
    dias = Column(Integer, nullable=False)

    chamados_recorrentes = relationship("ChamadoRecorrente", back_populates="frequencia")


class Usuario(Base, SoftDeleteMixin):
    """Tabela de usuários do sistema."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    role = relationship("Role", back_populates="usuarios")

    created_at = Column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
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


class Empresa(Base, SoftDeleteMixin):
    """Tabela das empresas/empregadores/clientes."""
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), unique=True, index=True, nullable=False)

    created_at = Column(
        TIMESTAMP, nullable=False, server_default=func.now()
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
    ativo = Column(Boolean, nullable=False, default=True)

    chamados = relationship("Chamado", back_populates="origem")
    chamados_recorrentes = relationship("ChamadoRecorrente", back_populates="origem")


class Chamado(Base, SoftDeleteMixin):
    """Tabela principal de chamados técnicos."""
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, index=True)
    responsavel_atendimento_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    responsavel_acao_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=False, index=True)
    tipo_maquina_id = Column(Integer, ForeignKey("maquinas.id"), nullable=True, index=True)
    origem_id = Column(Integer, ForeignKey("origens_problema.id"), nullable=True, index=True)
    datetime_abertura = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    contato = Column(String(150), nullable=False, index=True)
    porta_ssh = Column(String(100), nullable=True)
    relato = Column(Text, nullable=False)
    prioridade_id = Column(Integer, ForeignKey("prioridades.id"), nullable=True, index=True)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=True, index=True)
    acao_realizada = Column(Text, nullable=True)
    prioridade = relationship("Prioridade", back_populates="chamados", lazy="joined")
    status = relationship("Status", back_populates="chamados", lazy="joined")
    responsavel_atendimento = relationship("Usuario",
    foreign_keys=[responsavel_atendimento_id],
    back_populates="chamados_atendimento", lazy="joined")
    responsavel_acao = relationship("Usuario", foreign_keys=[responsavel_acao_id], back_populates="chamados_acao", lazy="joined")
    empresa = relationship("Empresa", back_populates="chamados", lazy="joined")
    tipo_maquina = relationship("Maquina", back_populates="chamados", lazy="joined")
    origem = relationship("OrigemProblema", back_populates="chamados", lazy="joined")
    logs = relationship("LogAcao", back_populates="chamado", lazy="joined")
    anexos = relationship("Anexo", back_populates="chamado")
    interacoes = relationship("Interacao", back_populates="chamado")
    tags = relationship("Tag",secondary=chamados_tags, back_populates="chamados")

class ChamadoRecorrente(Base, SoftDeleteMixin):
    """Tabela de chamados recorrentes, gerenciando frequências e próximas execuções."""
    __tablename__ = "chamados_recorrentes"

    id = Column(Integer, primary_key=True, index=True)

    cliente = Column(String(150), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True)
    porta_ssh = Column(String(100), nullable=True)
    tipo_maquina_id = Column(Integer, ForeignKey("maquinas.id"), nullable=True)
    relato = Column(Text, nullable=False)

    prioridade_id = Column(Integer, ForeignKey("prioridades.id"), nullable=True)
    prioridade = relationship("Prioridade")

    origem_id = Column(Integer, ForeignKey("origens_problema.id"), nullable=True)
    responsavel_atendimento_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    responsavel_acao_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    acao_realizada = Column(Text, nullable=True)

    frequencia_id = Column(Integer, ForeignKey("frequencias.id"), nullable=False)
    frequencia = relationship("Frequencia", back_populates="chamados_recorrentes")

    proxima_execucao = Column(DateTime(timezone=True), nullable=False)

    empresa = relationship("Empresa", back_populates="chamados_recorrentes")
    tipo_maquina = relationship("Maquina", back_populates="chamados_recorrentes")
    origem = relationship("OrigemProblema", back_populates="chamados_recorrentes")


class LogAcao(Base, SoftDeleteMixin):
    """Tabela para armazenar logs das ações realizadas por usuários em chamados."""
    __tablename__ = "log_acoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    chamado_id = Column(Integer, ForeignKey("chamados.id"), nullable=True)

    acao = Column(String, nullable=False)
    data_hora = Column(TIMESTAMP, nullable=False, server_default=func.now())

    tipo = Column(String, nullable=True)
    campo = Column(String, nullable=True)
    valor_antigo = Column(Text, nullable=True)
    valor_novo = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="log_acoes")
    chamado = relationship("Chamado", back_populates="logs")


class Anexo(Base, SoftDeleteMixin):
    """Tabela para armazenar metadados de arquivos anexados aos chamados."""
    __tablename__ = "anexos"

    id = Column(Integer, primary_key=True, index=True)
    chamado_id = Column(Integer, ForeignKey("chamados.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Quem fez o upload

    nome_arquivo_original = Column(String(255), nullable=False)
    path_arquivo_armazenado = Column(String(255), nullable=False, unique=True)
    content_type = Column(String(100), nullable=False)
    tamanho_bytes = Column(Integer, nullable=False)
    data_upload = Column(TIMESTAMP, nullable=False, server_default=func.now())

    chamado = relationship("Chamado", back_populates="anexos")
    usuario = relationship("Usuario")

class Interacao(Base, SoftDeleteMixin):
    """Tabela para armazenar a timeline de comentários e interações em um chamado."""
    __tablename__ = "interacoes"

    id = Column(Integer, primary_key=True, index=True)
    chamado_id = Column(Integer, ForeignKey("chamados.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Quem comentou

    comentario = Column(Text, nullable=False)
    privado = Column(Boolean, default=False, nullable=False) # True para notas internas
    data_interacao = Column(TIMESTAMP, nullable=False, server_default=func.now())

    chamado = relationship("Chamado", back_populates="interacoes")
    usuario = relationship("Usuario")

class Tag(Base):
    """Tabela de tags para categorização flexível de chamados."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)

    chamados = relationship(
        "Chamado",
        secondary=chamados_tags,
        back_populates="tags"
    )

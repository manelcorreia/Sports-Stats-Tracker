from abc import ABC, abstractmethod

# 1. ABCs (Contratos Formais) - (ISP Preservado)
class EstatisticaChave(ABC):    # ABC identificada na AF5.1
    @abstractmethod
    def obter_estatistica_chave(self, chave: str) -> int:
        """Retorna o valor de uma estatistica chave (DIP)"""
        pass

class RegistoEmJogo(ABC):       # ABC identificada na AF5.1
    """Protocolo para qualquer objeto que possa ser afetado por um evento de jogo."""
    @abstractmethod
    def processar_evento(self, tipo_evento, **kwargs):
        """Atualiza as estatísticas do objeto com base no tipo de evento (OCP)"""
        pass

class ExportavelJSON (ABC):
    @abstractmethod
    def to_json_dict(self) -> dict:
        pass
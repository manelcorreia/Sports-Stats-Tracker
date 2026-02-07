import datetime

# implementação transversal
class JSONMixin:
    def to_json_dict(self) -> dict:
        dados = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        dados['tipo_classe'] = self.__class__.__name__   # adiciona o nome da classe para saber o tipo no JSON
        return data

""" Mixin que regista alterações de estado."""
class AuditoriaMixin:
    def __init__(self, **kwargs):   # chama o próximo na MRO (cooperação)
        super().__init__(**kwargs)
        self.historico_logs = []

    def registar_log(self, mensagem: str):
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}"
        self.historico_logs.append(log_entry)

import random
from datetime import datetime, timedelta
from typing import Dict, List

class MockDataGenerator:
    """Serviço para gerar dados mockados de alertas automáticos"""
    
    # Dados mockados para geração de alertas
    UNIDADES = [
        "Unidade Barra Bonita",
        "Unidade Lençóis Paulista", 
        "Unidade Macatuba",
        "Unidade Pederneiras",
        "Unidade Bauru"
    ]
    
    FRENTES = [
        "Frente de Colheita",
        "Frente de Plantio",
        "Frente de Manutenção",
        "Frente de Transporte",
        "Frente de Armazenamento"
    ]
    
    EQUIPAMENTOS = [
        {"nome": "Colheitadeira JD9870", "codigo": "EQ001"},
        {"nome": "Trator Case IH", "codigo": "EQ002"},
        {"nome": "Plantadeira John Deere", "codigo": "EQ003"},
        {"nome": "Caminhão Scania", "codigo": "EQ004"},
        {"nome": "Silo de Armazenamento", "codigo": "EQ005"}
    ]
    
    TIPOS_OPERACAO = [
        "Manutenção Preventiva",
        "Manutenção Corretiva", 
        "Operação de Colheita",
        "Operação de Plantio",
        "Inspeção de Equipamento"
    ]
    
    OPERACOES = [
        "Troca de Filtro de Ar",
        "Troca de Óleo",
        "Ajuste de Sistema Hidráulico",
        "Limpeza de Radiador",
        "Verificação de Freios",
        "Calibração de Sensores",
        "Substituição de Correias",
        "Manutenção de Motor",
        "Verificação de Pneus",
        "Limpeza de Sistema de Combustível"
    ]
    
    PROBLEMAS = [
        "Equipamento apresentando baixa eficiência",
        "Vazamento de óleo identificado",
        "Sistema hidráulico com ruído anormal",
        "Temperatura elevada no motor",
        "Falha no sistema de freios",
        "Sensores com leitura incorreta",
        "Correias desgastadas",
        "Consumo excessivo de combustível",
        "Pneus com desgaste irregular",
        "Sistema de arrefecimento com problemas"
    ]
    
    @classmethod
    def generate_alert_data(cls) -> Dict:
        """Gera dados completos para um alerta automático"""
        
        # Seleciona dados aleatórios
        unidade = random.choice(cls.UNIDADES)
        frente = random.choice(cls.FRENTES)
        equipamento = random.choice(cls.EQUIPAMENTOS)
        tipo_operacao = random.choice(cls.TIPOS_OPERACAO)
        operacao = random.choice(cls.OPERACOES)
        problema = random.choice(cls.PROBLEMAS)
        
        # Gera código único
        codigo = random.randint(10000, 99999)
        
        # Gera data/hora realista (últimas 24 horas)
        data_operacao = datetime.now() - timedelta(
            hours=random.randint(0, 24),
            minutes=random.randint(0, 59)
        )
        
        # Calcula tempo de abertura
        tempo_abertura = datetime.now() - data_operacao
        tempo_abertura_str = f"{tempo_abertura.seconds // 3600}h {(tempo_abertura.seconds % 3600) // 60}min"
        
        return {
            "status": "Pendente",
            "codigo": str(codigo),  # Convertido para string
            "unidade": unidade,
            "frente": frente,
            "equipamento": equipamento["nome"],
            "codigo_equipamento": equipamento["codigo"],
            "tipo_operacao": tipo_operacao,
            "operacao": operacao,
            "nome_operador": "Rafael Cabral",
            "data_operacao": data_operacao.isoformat(),  # Formato ISO para compatibilidade
            "tempo_abertura": tempo_abertura_str,
            "tipo_arvore": "Árvore de Manutenção",
            "justificativa": None,  # Campo não preenchido automaticamente
            "prazo": None,  # Campo preenchido pelo líder via Telegram
            "nome_lider": "Rafael Cabral",
            "chat_id": "6435800936",
            "problema": f"[AUTO] {equipamento['nome']} - {operacao} - {problema}"  # Adicionado campo problema
        }
    
    @classmethod
    def generate_multiple_alerts(cls, count: int = 1) -> List[Dict]:
        """Gera múltiplos alertas"""
        return [cls.generate_alert_data() for _ in range(count)] 
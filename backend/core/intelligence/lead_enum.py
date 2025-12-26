# backend/core/intelligence/lead_enum.py
from enum import Enum

class LeadStage(Enum):
    HOT = ("HOT", "Khách hàng rất nóng, có khả năng mua cao")
    WARM = ("WARM", "Khách hàng quan tâm, cần follow thêm")
    QUALIFIED = ("QUALIFIED", "Khách đã đủ điều kiện, cần tư vấn")

    def __init__(self, code, description):
        self._code = code
        self._description = description

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description

    def __str__(self):
        return self.code

class LeadClassification(Enum):
    NGHIEN_NANG = ("nghien_nang", "Khách có nhu cầu cao, vấn đề rõ ràng")
    VIP = ("vip", "Khách VIP, giá trị cao")
    STRESS = ("stress", "Khách đang căng thẳng, cần tư vấn gấp")

    def __init__(self, code, description):
        self._code = code
        self._description = description

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description

    def __str__(self):
        return self.code

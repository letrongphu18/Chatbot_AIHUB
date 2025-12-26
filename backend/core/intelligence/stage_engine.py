from backend.core.intelligence.lead_enum import LeadClassification, LeadStage

def determine_stage(phone, email, classification, intent):
    classification = (classification or "").lower()
    intent = (intent or "").lower()

    if phone or email:
        return LeadStage.HOT
        #return "HOT"

    # 2️⃣ Có tín hiệu mua → WARM
    if (
        LeadClassification.VIP.code in classification
        or LeadClassification.NGHIEN_NANG.code in classification
        or "muon_mua" in intent
        or "warm" in intent
    ):
        return LeadStage.WARM

    # 3️⃣ Có phân loại nhưng chưa đủ nóng → QUALIFIED
    if classification and classification != "unknown":
        return LeadStage.QUALIFIED

    return None

    # if "warm" in classification or "muon_mua" in intent:
    #     return "WARM"

    # if classification and classification != "unknown":
    #     return "QUALIFIED"

    # return "NEW"

import sys
import json
from datetime import datetime

class SmartEnergyOptimizer:
    def __init__(self, battery_capacity_kwh=13.5, current_charge_pct=50.0):
        self.capacity = battery_capacity_kwh
        self.charge = (current_charge_pct / 100.0) * self.capacity

    def calculate_action(self, current_price_per_kwh, solar_generation_kw, load_demand_kw):
        """
        يحدد قرار إدارة الطاقة بناءً على السعر الحالي، توليد الطاقة الشمسية، والطلب.
        """
        net_energy = solar_generation_kw - load_demand_kw
        
        # إذا كان السعر منخفضاً جداً أو هناك فائض شمسي، اشحن البطارية
        if current_price_per_kwh < 0.15 or net_energy > 0:
            action = "STORE_ENERGY"
            reason = "طاقة شمسية فائضة أو أسعار شبكة منخفضة للغاية."
        # إذا كان السعر مرتفعاً والطلب أعلى من التوليد، قم بالتفريغ
        elif current_price_per_kwh > 0.30 and net_energy < 0:
            action = "DISCHARGE_BATTERY"
            reason = "أسعار الشبكة مرتفعة؛ استخدام طاقة البطارية المخزنة لتوفير التكاليف."
        else:
            action = "GRID_PASS_THROUGH"
            reason = "العمليات ضمن المعدلات العادية، الاعتماد على الشبكة أو التوازن المباشر."

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "reason": reason,
            "current_price": current_price_per_kwh,
            "net_solar_kw": net_energy
        }

def run_self_test():
    print("Running SmartEnergyOptimizer Self-Test...")
    optimizer = SmartEnergyOptimizer(battery_capacity_kwh=10.0, current_charge_pct=40.0)
    
    # اختبار حالة أسعار مرتفعة وعجز طاقة
    result = optimizer.calculate_action(current_price_per_kwh=0.35, solar_generation_kw=1.0, load_demand_kw=4.0)
    print("Test Result 1:", json.dumps(result, indent=2))
    assert result["action"] == "DISCHARGE_BATTERY", "فشل اختبار تفريغ البطارية!"

    # اختبار حالة طاقة شمسية فائضة
    result2 = optimizer.calculate_action(current_price_per_kwh=0.20, solar_generation_kw=5.0, load_demand_kw=2.0)
    print("Test Result 2:", json.dumps(result2, indent=2))
    assert result2["action"] == "STORE_ENERGY", "فشل اختبار تخزين الطاقة!"

    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        # التشغيل الافتراضي النموذجي
        opt = SmartEnergyOptimizer()
        sample_decision = opt.calculate_action(0.25, 2.0, 2.5)
        print(json.dumps(sample_decision, indent=2))

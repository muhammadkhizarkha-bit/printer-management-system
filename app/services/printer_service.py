from sqlalchemy.orm import Session
from ..models.printer import Printer

DEFAULT_PRINTERS = [
    ("HP LaserJet Pro M404", "Printer", 299.0, 12, "Compact monochrome laser printer."),
    ("Canon PIXMA G3020", "Printer", 199.0, 8, "All-in-one ink tank printer."),
    ("HP 26A Toner Cartridge", "Cartridge", 89.0, 30, "Black original toner cartridge."),
    ("Canon 047 Toner", "Cartridge", 75.0, 25, "Compatible black toner."),
    ("PCR Roller HP M402", "PCR", 12.5, 50, "Primary charge roller replacement."),
    ("Charger Roller HP 1020", "Charger Roller", 9.5, 40, "OEM charger roller."),
    ("Drum Unit Brother DR-2255", "Drum", 65.0, 15, "12,000 page yield drum unit."),
    ("Wiper Blade HP M402", "Blade", 7.0, 60, "Replacement wiper blade."),
]


def seed_printers(db: Session) -> None:
    if db.query(Printer).count() > 0:
        return
    for name, cat, price, stock, desc in DEFAULT_PRINTERS:
        db.add(Printer(name=name, category=cat, price=price, stock=stock, description=desc, image=""))
    db.commit()

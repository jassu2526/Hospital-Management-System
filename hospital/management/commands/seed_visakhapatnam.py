from django.core.management.base import BaseCommand
from hospital.models import Hospital, Room


VISAKHAPATNAM_HOSPITALS = [
    ("King George Hospital (KGH)", "Maharani Peta, Visakhapatnam"),
    ("Apollo Hospitals - Vizag", "Health City, Arilova, Visakhapatnam"),
    ("Care Hospitals - Vizag", "Ram Nagar, Visakhapatnam"),
    ("SevenHills Hospital - Vizag", "Rockdale Layout, Waltair Main Road, Visakhapatnam"),
    ("Omega Hospitals - Vizag", "Kommadi, Madhurawada, Visakhapatnam"),
    ("Shankar Eye Hospital - Vizag", "Seethammadhara, Visakhapatnam"),
    ("GITAM Hospital", "Rushikonda, Visakhapatnam"),
    ("Vizag Kidney and Urology Centre", "Seethammadhara, Visakhapatnam"),
]


class Command(BaseCommand):
    help = "Seed hospitals and rooms for Visakhapatnam, Andhra Pradesh"

    def handle(self, *args, **options):
        created = 0
        for name, addr in VISAKHAPATNAM_HOSPITALS:
            h, is_new = Hospital.objects.get_or_create(
                name=name,
                defaults={'address': addr, 'city': 'Visakhapatnam', 'state': 'Andhra Pradesh'},
            )
            if not is_new:
                h.address = addr
                h.city = 'Visakhapatnam'
                h.state = 'Andhra Pradesh'
                h.save()
            # Ensure some rooms
            for rn, cap in (('A1', 12), ('B1', 16), ('ICU-1', 8)):
                Room.objects.get_or_create(hospital=h, name=rn, defaults={'capacity': cap})
            created += 1 if is_new else 0
        total = Hospital.objects.filter(city='Visakhapatnam').count()
        self.stdout.write(self.style.SUCCESS(f'Seeded Visakhapatnam hospitals. New: {created}, Total: {total}'))

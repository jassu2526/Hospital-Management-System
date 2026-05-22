from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import Profile, Doctor, Patient, Attendant, Shift
from hospital.models import Hospital, Room


class Command(BaseCommand):
    help = "Create a user with role and optional hospital/room/shift"

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--email', default='')
        parser.add_argument('--first_name', default='')
        parser.add_argument('--last_name', default='')
        parser.add_argument('--role', required=True, choices=['ADMIN', 'DOCTOR', 'PATIENT', 'ATTENDANT'])
        parser.add_argument('--hospital', default='')
        parser.add_argument('--room', default='')
        parser.add_argument('--shift', default='', choices=['MORNING', 'AFTERNOON', 'NIGHT', ''])
        parser.add_argument('--specialization', default='')
        parser.add_argument('--age', type=int, default=None)
        parser.add_argument('--room_capacity', type=int, default=0)

    def handle(self, *args, **options):
        username = options['username']
        if User.objects.filter(username=username).exists():
            raise CommandError('Username already exists')
        user = User.objects.create(
            username=username,
            email=options['email'],
            first_name=options['first_name'],
            last_name=options['last_name'],
        )
        user.set_password(options['password'])
        role = options['role']
        if role == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        user.save()

        Profile.objects.create(user=user, role=role)

        hospital_name = options['hospital'].strip()
        room_name = options['room'].strip()
        shift_name = options['shift'].strip()

        hospital_obj = None
        room_obj = None
        shift_obj = None

        if hospital_name:
            hospital_obj, _ = Hospital.objects.get_or_create(name=hospital_name)
        if room_name:
            if not hospital_obj:
                raise CommandError('Room requires hospital')
            capacity = options['room_capacity'] or 0
            room_obj, _ = Room.objects.get_or_create(hospital=hospital_obj, name=room_name, defaults={'capacity': capacity})
        if shift_name:
            if shift_name:
                if not Shift.objects.filter(name=shift_name).exists():
                    if shift_name == 'MORNING':
                        Shift.objects.create(name='MORNING', start_time='06:00', end_time='14:00')
                    elif shift_name == 'AFTERNOON':
                        Shift.objects.create(name='AFTERNOON', start_time='14:00', end_time='22:00')
                    elif shift_name == 'NIGHT':
                        Shift.objects.create(name='NIGHT', start_time='22:00', end_time='06:00')
            shift_obj = Shift.objects.get(name=shift_name) if shift_name else None

        if role == 'DOCTOR':
            if not hospital_obj:
                raise CommandError('Doctor requires hospital')
            Doctor.objects.create(user=user, hospital=hospital_obj, specialization=options['specialization'])
        elif role == 'PATIENT':
            if not hospital_obj:
                raise CommandError('Patient requires hospital')
            Patient.objects.create(user=user, hospital=hospital_obj, room=room_obj, age=options['age'])
        elif role == 'ATTENDANT':
            if not hospital_obj or not room_obj or not shift_obj:
                raise CommandError('Attendant requires hospital, room, and shift')
            Attendant.objects.create(user=user, hospital=hospital_obj, room=room_obj, shift=shift_obj)

        self.stdout.write(self.style.SUCCESS(f'User {username} created with role {role}'))

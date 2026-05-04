#!/usr/bin/env python

import os
import sys

# ✅ Set Django settings before importing any Django module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pneumonia_detection.settings')

import django
django.setup()

# Now import Django models
from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from django.core.management import execute_from_command_line

from main.models import Patient, XRay, Report


def create_groups():
    """Create user groups"""
    groups = ['Admin', 'Doctor', 'Lab Technician']
    for group_name in groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✓ Created group: {group_name}")

def create_users():
    """Create sample users"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@hospital.com',
            'password': 'admin123',
            'first_name': 'System',
            'last_name': 'Administrator',
            'is_staff': True,
            'is_superuser': True,
            'group': 'Admin'
        },
        {
            'username': 'doctor1',
            'email': 'doctor1@hospital.com',
            'password': 'password',
            'first_name': 'Dr. Sarah',
            'last_name': 'Johnson',
            'is_staff': True,
            'group': 'Doctor'
        },
        {
            'username': 'doctor2',
            'email': 'doctor2@hospital.com',
            'password': 'password',
            'first_name': 'Dr. Michael',
            'last_name': 'Chen',
            'is_staff': True,
            'group': 'Doctor'
        },
        {
            'username': 'lab1',
            'email': 'lab1@hospital.com',
            'password': 'password',
            'first_name': 'Lab Tech',
            'last_name': 'Smith',
            'is_staff': True,
            'group': 'Lab Technician'
        },
        {
            'username': 'lab2',
            'email': 'lab2@hospital.com',
            'password': 'password',
            'first_name': 'Lab Tech',
            'last_name': 'Williams',
            'is_staff': True,
            'group': 'Lab Technician'
        }
    ]
    
    for user_data in users_data:
        group_name = user_data.pop('group')
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            
            # Add to group
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            
            print(f"✓ Created user: {user.username} ({group_name})")

def create_sample_patients():
    """Create sample patients"""
    patients_data = [
        {
            'name': 'Emma Thompson',
            'date_of_birth': datetime.now().date() - timedelta(days=365*5),  # 5 years old
            'gender': 'F',
            'guardian_name': 'Sarah Thompson',
            'phone': '+1-555-0101',
            'email': 'sarah.thompson@email.com',
            'address': '123 Main St, Springfield, IL 62701',
            'medical_history': 'No significant medical history. Regular checkups.'
        },
        {
            'name': 'Liam Rodriguez',
            'date_of_birth': datetime.now().date() - timedelta(days=365*3),  # 3 years old
            'gender': 'M',
            'guardian_name': 'Maria Rodriguez',
            'phone': '+1-555-0102',
            'email': 'maria.rodriguez@email.com',
            'address': '456 Oak Ave, Springfield, IL 62702',
            'medical_history': 'Mild asthma, uses inhaler as needed.'
        },
        {
            'name': 'Sophia Chen',
            'date_of_birth': datetime.now().date() - timedelta(days=365*7),  # 7 years old
            'gender': 'F',
            'guardian_name': 'David Chen',
            'phone': '+1-555-0103',
            'email': 'david.chen@email.com',
            'address': '789 Pine St, Springfield, IL 62703',
            'medical_history': 'Allergic to penicillin. Previous pneumonia at age 4.'
        },
        {
            'name': 'Noah Johnson',
            'date_of_birth': datetime.now().date() - timedelta(days=365*2),  # 2 years old
            'gender': 'M',
            'guardian_name': 'Jennifer Johnson',
            'phone': '+1-555-0104',
            'email': 'jennifer.johnson@email.com',
            'address': '321 Elm St, Springfield, IL 62704',
            'medical_history': 'Premature birth. Regular monitoring required.'
        },
        {
            'name': 'Olivia Davis',
            'date_of_birth': datetime.now().date() - timedelta(days=365*6),  # 6 years old
            'gender': 'F',
            'guardian_name': 'Robert Davis',
            'phone': '+1-555-0105',
            'email': 'robert.davis@email.com',
            'address': '654 Maple Ave, Springfield, IL 62705',
            'medical_history': 'No known allergies. Healthy child.'
        }
    ]
    
    for patient_data in patients_data:
        patient, created = Patient.objects.get_or_create(
            name=patient_data['name'],
            defaults=patient_data
        )
        if created:
            print(f"✓ Created patient: {patient.name} (ID: {patient.patient_id})")

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Database migrations completed")

def main():
    """Main setup function"""
    print("🏥 Child Pneumonia Detection System - Database Setup")
    print("=" * 60)
    
    try:
        # Run migrations
        run_migrations()
        
        # Create groups
        print("\n👥 Creating user groups...")
        create_groups()
        
        # Create users
        print("\n👤 Creating sample users...")
        create_users()
        
        # Create patients
        print("\n🧒 Creating sample patients...")
        create_sample_patients()
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("\n📋 Login Credentials:")
        print("   Admin: admin / admin123")
        print("   Doctor: doctor1 / password")
        print("   Lab Tech: lab1 / password")
        print("\n🚀 You can now run: python manage.py runserver")
        print("   Access the application at: http://127.0.0.1:8000/")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

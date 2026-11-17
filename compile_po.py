import os
import django
from django.conf import settings
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tazar.settings')
django.setup()

print("Компилируем переводы...")
try:
    # Вызываем через стандартный call_command без лишних внутренних аргументов
    call_command('compilemessages')
    print("Готово! Все файлы успешно скомпилированы.")
except Exception as e:
    print(f"Ошибка компиляции: {e}")

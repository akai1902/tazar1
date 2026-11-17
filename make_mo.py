import polib
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
locales = ['en', 'ky']

for lang in locales:
    po_path = os.path.join(base_dir, 'locale', lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(base_dir, 'locale', lang, 'LC_MESSAGES', 'django.mo')

    if os.path.exists(po_path):
        print(f"Компилирую {lang}...")
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)  # <-- вот здесь исправили на save_as_mofile
        print(f"Готово: {mo_path}")
    else:
        print(f"Файл {po_path} не найден.")
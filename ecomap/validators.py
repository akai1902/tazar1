from urllib.parse import urlsplit

from django.core.exceptions import ValidationError

# Ссылки на видео принимаем ТОЛЬКО с этих сайтов (сами домены и их поддомены).
# Нужен ещё сайт: добавь его в этот список.
ALLOWED_VIDEO_HOSTS = ('youtube.com', 'youtu.be', 'vimeo.com', 'tiktok.com', 'instagram.com')

# «Перенаправляющие» адреса на разрешённых сайтах: через них можно уйти на чужой сайт
BLOCKED_PATH_PREFIXES = ('/redirect', '/attribution_link')


def validate_video_url(value):
    """Белый список: только https и только известные видеосервисы."""
    if not value:
        return

    parts = urlsplit(value.strip())
    try:
        port = parts.port
    except ValueError:
        raise ValidationError('Недопустимая ссылка.')

    host = (parts.hostname or '').lower()
    if parts.scheme != 'https':
        raise ValidationError('Ссылка должна начинаться с https://')
    if parts.username or parts.password or port not in (None, 443):
        raise ValidationError('Недопустимая ссылка.')

    # проверяем домен целиком: «youtube.com.evil.com» и «evil.com/?youtube.com» не пройдут
    if not any(host == h or host.endswith('.' + h) for h in ALLOWED_VIDEO_HOSTS):
        raise ValidationError('Разрешены ссылки только на YouTube, Vimeo, TikTok и Instagram.')
    if parts.path.lower().startswith(BLOCKED_PATH_PREFIXES):
        raise ValidationError('Недопустимая ссылка.')

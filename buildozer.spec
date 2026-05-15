[app]

# Название приложения
title = NEVPN

# Имя пакета (только строчные, без пробелов)
package.name = nevpn

# Домен пакета
package.domain = org.nevpn

# Папка с исходниками
source.dir = .

# Расширения файлов которые включаем в APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

# Явно включаем папку с картинками
source.include_patterns = images/*.png,images/*.jpg

# Версия
version = 1.0.0

# Зависимости Python
# kivymd должна совпадать с версией которую используешь
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,materialyoucolor,exceptiongroup

# Ориентация экрана
orientation = portrait

# Полноэкранный режим (без системной панели)
fullscreen = 0

# Иконка и сплэш-скрин
icon.filename = images/logo_icon.png
# presplash.filename = images/presplash.png

# Android разрешения
android.permissions = INTERNET

# Минимальная версия Android (5.0 = API 21)
android.minapi = 21

# Целевая версия Android
android.api = 34

# Версии SDK/NDK (Buildozer скачает автоматически)
android.ndk = 25b
android.sdk = 34

# Автоматически принять лицензии SDK
android.accept_sdk_license = True

# Архитектуры (arm64-v8a — современные телефоны, armeabi-v7a — старые)
android.archs = arm64-v8a, armeabi-v7a

# Логирование
log_level = 2

# Gradle зависимости (если нужны)
# android.gradle_dependencies =

# Отключить резервное копирование (опционально)
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 1

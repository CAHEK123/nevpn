[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg

version = 1.0.0

# ── СОВМЕСТИМОСТЬ kivy + NDK ───────────────────────────────
# Проблема: kivy==2.3.0 не компилируется с NDK r25b
#   error: too few arguments to function call, expected 6, have 5
#   (OpenGL ES функции изменились в NDK r23+)
#
# Решение: kivy==2.2.1 — последняя версия совместимая с NDK r25b
#          kivymd==1.1.1 — совместима с kivy 2.2.1
#
# Проверенная рабочая комбинация:
#   kivy==2.2.1 + kivymd==1.1.1 + NDK r25b
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow

orientation = portrait
fullscreen = 0

icon.filename = images/logo_icon.png

# Samsung A35 5G — Android 16 (API 36), One UI 8.0
android.permissions = INTERNET

android.minapi = 26
android.api = 33
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.enable_androidx = True

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

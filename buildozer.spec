[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg

version = 1.0.0

# Реальный хэш тега v2024.01.21 — последний релиз с Python 3.11
p4a.commit = 957a3e5

requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,pillow,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = images/logo_icon.png

# INTERNET — для VPN Gate API
# QUERY_ALL_PACKAGES — чтобы проверить наличие ics-openvpn
# READ_EXTERNAL_STORAGE — для доступа к .ovpn на Android < 10 (SAF не требует его на 10+)
android.permissions = INTERNET,QUERY_ALL_PACKAGES,READ_EXTERNAL_STORAGE

# FileProvider — нужен чтобы передать .ovpn файл в ics-openvpn как content:// URI.
# ВАЖНО: "android.add_providers" — это НЕ настоящая опция buildozer (запрос на
# такую фичу есть в issue-трекере p4a, но в текущем buildozer/p4a она не
# реализована и просто игнорируется при сборке — провайдер в манифест не
# попадал, поэтому FileProvider не работал). Ниже — реально существующие
# опции buildozer, которые делают то же самое:
android.add_resources = android/file_paths.xml:xml/file_paths.xml
android.extra_manifest_application_arguments = android/extra_manifest_application_arguments.xml

android.minapi = 26
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.enable_androidx = True

# Если сборка упадёт на "FileProvider class not found" — раскомментируйте:
# android.gradle_dependencies = androidx.core:core:1.12.0

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

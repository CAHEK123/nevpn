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
android.permissions = INTERNET,QUERY_ALL_PACKAGES

# FileProvider для передачи .ovpn файла в ics-openvpn (Android 7+)
android.manifest.placeholders = applicationId:org.nevpn

android.minapi = 26
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.enable_androidx = True

# FileProvider — добавляем в AndroidManifest через p4a хук
android.add_providers = org.nevpn.NevpnFileProvider:androidx.core.content.FileProvider

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

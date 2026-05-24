[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = image/*.png,image/*.jpg,image/*.jpeg

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow

orientation = portrait
fullscreen = 0

icon.filename = image/logo_icon.png

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.minapi = 26
android.api = 34
android.ndk = 25b
android.sdk = 34
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False

# p4a устанавливается через pip в workflow (python-for-android==2024.1.21)
# НЕ используем p4a.branch — buildozer передаёт значение в git clone -b БЕЗ префикса v,
# поэтому git не находит теги (они называются v2024.01.21, а не 2024.01.21)

[buildozer]
log_level = 2
warn_on_root = 1

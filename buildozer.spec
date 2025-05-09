[app]

# Настройки приложения
title = FTPhost
package.name = ftpserver
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
version = 1.0
requirements = python3==3.11.6, kivy==2.3.0, pyftpdlib==1.5.7, android, openssl

# Настройки Android
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0
android.api = 34
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.gradle_dependencies = 'com.android.support:multidex:1.0.3'

# Разрешения
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

# Особые настройки
android.allow_backup = True
android.arch = armeabi-v7a
p4a.branch = master
android.private_storage = True
android.wakelock = True
orientation = all


# Настройки сборки
log_level = 2
android.entrypoint = org.kivy.android.PythonActivity
android.meta_data = org.kivy.orientation=portrait
android.add_src = 
[app]
title = Restaurant ERP
package.name = restauranterp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0
android.api = 34
android.minapi = 21
android.ndk = 27c
android.accept_sdk_license = True

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Features
android.features = android.hardware.location,android.hardware.location.gps

requirements = python3,kivy,pillow,babel,reportlab,openpyxl

# Orientation
orientation = portrait

# Build
log_level = 2
warn_on_root = 1

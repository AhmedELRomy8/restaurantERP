[app]
title = Restaurant ERP
package.name = restauranterp
package.domain = org.restaurant.erp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0
requirements = python3,kivy,pillow,babel,reportlab,openpyxl

use_webview = 0
presplash.filename = %(source.dir)s/
icon.filename = %(source.dir)s/

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 34
android.minapi = 21
android.ndk = 27c
android.accept_sdk_license = True
android.release_artifact = aab

[app:android]
permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,ACCESS_FINE_LOCATION
features = android.hardware.location,android.hardware.location.gps
orientation = portrait
fullscreen = 0
android.arch = arm64-v8a

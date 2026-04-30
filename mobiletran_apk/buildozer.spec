[app]

# (str) Title of your application
title = MobileTran

# (str) Package name
package.name = mobiletran

# (str) Package domain (needed for android/ios packaging)
package.domain = com.mobiletran

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
source.include_patterns = *.py,*.png,*.kv

# (list) Source files to exclude (let empty to not exclude anything)
# source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
# source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
# source.exclude_patterns = license,images/*.jpg

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,requests,android

# (str) Custom source folders for requirements
# requirements.source.kivy = ../kivy

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# OSX Specific
#
#
author = MobileTran Team

# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats: #RRGGBB #AARRGGBB or 'red', 'blue'...
presplash_color = #f5f5f5

# (list) Permissions for the Android app
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

# (int) Android API to use
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 26

# (int) Target API your APK will support
android.targetapi = 34

# (str) Android SDK directory (if not set, buildozer will use custom directory)
# android.sdk_path = %(android.ndk_path)s/platforms

# (str) Android NDK directory (if not set, buildozer will use custom directory)
# android.ndk_path = %(android.sdk_path)s/ndk/25.2.9519653

# (str) Android NDK version (if not set, buildozer will use best matching)
# android.ndk_version = 25c

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android LogCat filters to use
# android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpypy.so symlink
# android.copy_libs = 1

# (str) The Android arch to build for. Choose from: aarch64_64, arm64-v8a, armeabi-v7a, x86, x86_64
android.archs = arm64-v8a

# (int) Number of threads to use for building the APK
android.num_threads = 4

# (str) Location of the Android AAR for the app
# android.add_aar =

# (bool) Indicate whether the application will be a library or not
# android.library_receivers =

# (str) Meta-data to add to AndroidManifest.xml
# android.meta_data =

# (str) Extra XML to add to AndroidManifest.xml
# android.extra_xml =

# (str) The Android package with which to embed the application
# android.add_src =

# (str) Extra libraries to add to the APK build
# android.add_libs_arm64 =

# (str) Java files to add to the libs directory
# android.add_jar_libs =

# (bool) Add gradle dependencies to the APK
# android.gradle_dependencies =

# (str) The path to a custom build python module
# android.build_tools_dir =

# (bool) Use the deprecated ant build instead of gradle
# android.ant_path = /usr/share/ant

# (str) Add extra Java arguments for ant
# android.ant_args =

# (str) Add extra arguments for the aapt packaging tool
# android.aapt_args =

# (str) Add extra arguments for the aapt2 packaging tool
# android.aapt2_args =

# (bool) Add extra intent filter to the Android app
# android.used_libs =

# (str) Add a specific jar to the libs, like a MPAndroidChart
# android.add_src =

# (str) Path to a custom AndroidManifest.xml
# android.manifest =

# (list) List of string extra arguments to add to the APK
# android.extra_java_args =

# (str) Path to a custom activity class
# android.activity_class_name =

# (str) The Android Java SDK root path
# android.java_path =

# (str) Path to the Android SDK directory
# android.sdk_path =

# (str) Path to the Android NDK directory
# android.ndk_path =

# (str) Android SDK build tools version
# android.build_tools = 34.0.0

# (bool) Use the deprecated ant build instead of gradle
# android.gradle_build = 1

# (str) Set the path to the gradlew executable in the build directory
# android.gradle_path =

# (str) Path to gradlew executable to use for building the APK
# android.gradle_cmd =

# (str) Path to Java compiler
# java_path =

# (list) Add a directory to the compilation
# android.add_src =

# (str) Python for Android - Directory for the toolchain
# p4a.dir =

# (str) Python for Android - Git URL of the toolchain (master)
# p4a.source_dir =

# (str) Python for Android - The branch to checkout
# p4a.branch =

# (list) Additional options to pass to python-for-android (p4a) build
# p4a.bootstrap = sdl2
# p4a.hooks = hooks
# p4a.env =

# (list) Requirements that cannot be installed via pip
# p4a.requirements =

# (bool) If True, the package will be compiled to a minimal version
# android.min_compression = 0

# iOS specific
#

# (str) Name of the certificate to use for signing the app
# ios.codesign.allowed =

# (str) Path to the iOS SDK
# ios.sdk_path =

# (str) Path to the iOS certificate
# ios.codesign.certificate =

# (str) Path to the iOS provisioning profile
# ios.codesign.provisioning_profile =

# (str) Path to the iOS mobile provision
# ios.codesign.mobile_provision =

# (str) Path to the iOS entitlements
# ios.codesign.entitlements =

# (str) Path to the iOS keychain
# ios.codesign.keychain =

# (str) Path to the iOS signing private key
# ios.codesign.signature =

# (str) Path to the iOS signing private key password
# ios.codesign.signature_password =

# (list) iOS frameworks to include
# ios.frameworks =

# (list) iOS private frameworks to include
# ios.private_frameworks =

# (str) iOS SDK version
# ios.sdk_version =

# (str) iOS minimum OS version
# ios.min_os_version =

# (str) iOS icon file
# ios.icon.file =

# (str) iOS icon file type
# ios.icon.type =

# (list) iOS frameworks to include
# ios.frameworks =

# (list) iOS permissions to set
# ios.permissions =

# (list) iOS team id
# ios.team_id =

# (bool) Use the debug mode for iOS
# ios.debug = 1

# (str) Path to the iOS Xcode project
# ios.project =

# (str) Name of the Xcode project
# ios.xcodeproj =

# (str) Path to the iOS project directory
# ios.project_dir =

# (str) The iOS app store id
# ios.appstore_id =

# (str) The iOS app store id for the app
# ios.appstore_id =

# (str) The iOS app store id for the app
# ios.appstore_id =

# (str) The iOS app store id for the app
# ios.appstore_id =

# (str) The iOS app store id for the app
# ios.appstore_id =

# (str) The iOS app store id for the app
# ios.appstore_id =

#
# Windows specific
#

# (str) Windows SDK version
# win.sdk_version =

# (str) Windows UWP sdk version
# win.uwp_sdk_version =

# (str) Windows SDK path
# win.sdk_path =

#
# macOS specific
#

# (str) macOS SDK version
# mac.sdk_version =

# (str) macOS minimum OS version
# mac.min_os_version =

# (str) macOS icon file
# mac.icon.file =

# (str) macOS icon file type
# mac.icon.type =

# (str) macOS project name
# mac.project_name =

#
# Build configuration
#

# (str) Build directory (default is ./build)
# build_dir = ./build

# (str) Bin directory (default is ./bin)
# bin_dir = ./bin

# (str) Android SDK directory
# android.sdk_path =

# (str) Android NDK directory
# android.ndk_path =

# (str) Android ANT directory
# android.ant_path =

# (str) Path to the Android SDK
# android.sdk_path =

# (str) Path to the Android NDK
# android.ndk_path =

# (str) Path to the Android Ant
# android.ant_path =

# (str) Path to the Python for Android
# p4a.dir =

# (str) Path to the Python for Android source
# p4a.source_dir =

# (str) Path to the Android SDK (deprecated)
# android.sdk_path =

# (str) Path to the Android NDK (deprecated)
# android.ndk_path =

# (str) Path to the Android Ant (deprecated)
# android.ant_path =

# (str) Path to the Python for Android (deprecated)
# p4a.dir =

# (str) Path to the Python for Android source (deprecated)
# p4a.source_dir =

# (list) List of services to declare
# services =

# (str) Path to the source dir
# source.dir =

# (list) List of service to declare
# services =

# (str) Path to the source dir
# source.dir =

# (list) List of service to declare
# services =

# (str) Path to the source dir
# source.dir =

# (list) List of service to declare
# services =

# (str) Path to the source dir
# source.dir =

# (list) List of service to declare
# services =

# (str) Path to the source dir
# source.dir =

# (list) List of service to declare
# services =

# (str) Path to the source dir
# source.dir =

# (list) List of service to declare
# services =


#
# Examples
#
# (str) Path to the example directory
# examples.dir =

# (str) Path to the examples source
# examples.source =

# (list) List of examples to include
# examples.include =

# (list) List of examples to exclude
# examples.exclude =

# (str) Path to the examples directory
# examples.dir =

# (str) Path to the examples source
# examples.source =

# (list) List of examples to include
# examples.include =

# (list) List of examples to exclude
# examples.exclude =


#
# Advanced
#

# (str) Path to the custom buildozer.spec
# spec.filename =

# (list) List of .spec files to include
# spec.include =

# (list) List of .spec files to exclude
# spec.exclude =

# (bool) Enable verbose logging
log_level = 2

# (bool) Add a check for updates
# check_for_updates = 0

# (str) Path to the build directory
# build_dir = ./build

# (str) Path to the bin directory
# bin_dir = ./bin

# (list) List of custom buildozer commands
# commands =

# (str) Path to the custom buildozer
# buildozer_path =

# (str) Path to the custom buildozer.spec
# spec.filename =

# (list) List of .spec files to include
# spec.include =

# (list) List of .spec files to exclude
# spec.exclude =


#
# Buildozer
#

# (str) Path to the buildozer executable
# buildozer_path = buildozer

# (str) Path to the buildozer.spec
# spec.filename = buildozer.spec
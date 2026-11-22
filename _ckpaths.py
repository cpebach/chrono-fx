import os

OLD = r"C:/Users/omicron/android-build"
print("C旧パス存在:", os.path.isdir(OLD))
if os.path.isdir(OLD):
    print("  中身:", sorted(os.listdir(OLD)))
for p in (r"C:/Users/omicron/android-build/android-sdk/platforms/android-34/android.jar",
          r"C:/Users/omicron/android-build/android-sdk/build-tools/34.0.0/aapt2.exe",
          r"C:/Users/omicron/android-build/jdk/bin/javac.exe",
          r"C:/Users/omicron/android-build/chronofx.keystore",
          r"D:/dev/android-build/jdk/bin/javac.exe",
          r"D:/dev/android-tools/Sdk/platforms/android-34/android.jar",
          r"D:/dev/android-tools/Sdk/build-tools/34.0.0/aapt2.exe",
          r"D:/dev/android-tools/jdk-17.0.21+9/bin/javac.exe",
          r"D:/dev/android-build/chronofx.keystore",
          r"D:/dev/android-tools/Sdk/cmdline-tools/latest/bin/sdkmanager.bat"):
    print(("OK " if os.path.exists(p) else "-- "), p)

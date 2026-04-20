@echo off
chcp 65001 >nul
echo ========================
echo 编译和运行Java签名工具
echo ========================

echo.
echo 1. 编译Java文件...
javac SignatureGenerator.java

if %ERRORLEVEL% neq 0 (
    echo ❌ 编译失败，请确保已安装Java JDK
    pause
    exit /b 1
)

echo ✅ 编译成功！
echo.

echo 2. 运行测试...
java SignatureGenerator

echo.
echo 3. 单独测试...
java TestSignature

echo.
echo ========================
echo 完成！
echo ========================
pause
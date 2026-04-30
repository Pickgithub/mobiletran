# 📤 上传代码到 GitHub 的完整操作步骤

请打开 **cmd**（按 `Win+R` → 输入 `cmd` → 回车），然后按顺序执行以下命令。

---

## 步骤 1：配置 Git 身份（第一次使用 Git 时需要）

```bash
cd d:\mobiletran

REM 替换成你的 GitHub 用户名和注册邮箱
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub注册邮箱"
```

**示例：**
```bash
git config --global user.name "zhangsan"
git config --global user.email "zhangsan@example.com"
```

---

## 步骤 2：创建 .gitignore（排除不需要上传的文件）

```bash
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo .buildozer/ >> .gitignore
echo bin/ >> .gitignore
echo .gradle/ >> .gitignore
```

---

## 步骤 3：初始化仓库并提交

```bash
git init
git add .
git commit -m "init: MobileTran 翻译工具初始版本"
```

---

## 步骤 4：连接 GitHub 远程仓库

先去浏览器操作：
```
1. 打开 https://github.com 并登录
2. 点右上角 + → New repository
3. Repository name 输入：mobiletran
4. 点最下面的绿色按钮 "Create repository"
5. 创建后页面中会显示一个地址，复制它（类似下面）：
   https://github.com/你的用户名/mobiletran.git
```

然后回到 cmd，执行：

```bash
REM 把下面的地址替换成你复制的地址
git remote add origin https://github.com/你的用户名/mobiletran.git
```

---

## 步骤 5：推送到 GitHub

```bash
REM 推送到 GitHub（会弹出登录窗口）
git push -u origin main
```

### 如果 push 失败，说明需要登录

Git 会弹出一个 GitHub 登录窗口。但 GitHub 在 2021 年后**不再支持密码登录**，需要用 **Personal Access Token（个人访问令牌）**：

**生成 Token 的方法：**

```
1. 打开 https://github.com/settings/tokens
2. 点 "Generate new token (classic)"
3. 勾选 repo（所有权限）
4. 拉到页面底部点 "Generate token"
5. 复制生成的一串字母数字（如：ghp_xxxxxxxxxxxxxxxxxxxx）
   ★ 关闭页面后就看不到了，请先保存在记事本里
```

**使用 Token 登录：**

```
6. 回到 cmd 中，执行 git push -u origin main
7. 弹出的登录窗口中：
   - Username: 输入你的 GitHub 用户名
   - Password: 输入刚才复制的 Token（不是你的登录密码）
8. 点 Sign in
```

---

## 步骤 6：验证上传成功

打开浏览器访问：
```
https://github.com/你的用户名/mobiletran
```

应该能看到所有文件已上传。

---

## 步骤 7（可选）：设置 GitHub Actions 自动构建 APK

文件上传成功后：

```
1. 在 GitHub 仓库页面，点顶部导航栏的 Actions 选项卡
2. 点 "set up a workflow yourself"
3. 将下面内容完整复制粘贴进去（覆盖默认内容）：
```

```yaml
name: Build APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y python3-pip python3-dev zlib1g-dev libffi-dev
          pip3 install --upgrade pip buildozer cython
      - name: Build APK
        run: cd mobiletran_apk && buildozer android debug
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: mobiletran-apk
          path: mobiletran_apk/bin/*.apk
```

```
4. 点 "Commit changes"（绿色按钮）
5. 等 15-30 分钟，Actions 页面会显示构建进度
6. 构建完成后，点进该工作流，下面有 Artifacts 可下载 .apk 文件
```

---

## 📌 常见问题

| 问题 | 解决方法 |
|------|---------|
| `git push` 弹出登录窗口但密码错误 | 用上面方法生成 **Personal Access Token**，在密码框粘贴 Token |
| `git remote add origin ...` 报错 | 说明已经添加过，执行 `git remote set-url origin 你的地址` |
| `git commit` 提示 unknown author | 检查步骤1是否执行成功，重新配置 user.name 和 user.email |
| 上传后 Actions 不自动构建 | 检查是否已添加 .yml 文件到 .github/workflows/ 目录 |
| 构建失败 | 在 GitHub Actions 页面点进失败的工作流，查看红色日志信息 |
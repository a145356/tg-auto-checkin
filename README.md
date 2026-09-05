# 🚀 Telegram Serverless 个人号全自动准时签到系统

这是一个基于 **Cloudflare Workers**（秒级准时闹钟）与 **GitHub Actions**（轻量级执行枪手）联动实现的 Telegram 个人号（UserBot）自动签到系统。

### 🌟 项目核心优势
* 💰 **100% 纯白嫖**：完全免绑定信用卡，免购买云服务器/VPS。
* ⏰ **秒级准时，绝不漏签**：用 Cloudflare 毫秒级定时器从外部主动“推”唤醒信号，彻底解决 GitHub Actions 自带 Cron 定时严重排队、延迟和漏签的灾难。
* 🔄 **永不休眠停摆**：通过外部 API 天天互动，彻底打破 GitHub 对冷门 0 活跃项目连续 60 天自动关停定时任务的限制。
* 🔒 **安全保护**：采用**公有仓库（Public）**托管代码，核心隐私凭证（账号、密钥、Session、群组ID）100% 抽离并锁进 GitHub Secrets 加密保险箱，全网无泄露风险。

---

## 🛠️ 整体架构原理

```text
[ Cloudflare Workers (定时器) ] 
       │ (到点准时通过 API 发送加密暗号)
       ▼
[ GitHub Actions (执行环境) ] 
       │ (被闪电唤醒，分配临时服务器)
       ├─► 1. 读取 Secrets 并将 Base64 文本还原为本地电报 .session 文件
       ├─► 2. 启动轻量 Python 脚本，通过内置的 Telethon 库连接电报
       ├─► 3. 依次向指定的机器人/群组发送签到消息（如：/checkin）
       └─► 4. 彻底断开连接，容器自毁（全程仅需 10-15 秒，极速不浪费额度）
```

---

## 📖 部署与操作指南

### 第一步：在本地/服务器提取电报 Base64 凭证
由于云端环境是临时的，必须在本地或通过 SSH 登录 Linux 服务器，运行一次 Telethon 的登录脚本（输入手机号与验证码），登录成功后将生成的 `session/xxxx.session` 文件，通过 Python 的 `base64` 库转换成一长串 **Base64 加密乱码文本**，复制保存到记事本备用。
> ⚠️ **注意**：切勿将本地生成的 `session/` 文件夹及含有明文密钥的登录脚本提交至 GitHub 仓库！

### 第二步：配置 GitHub Actions 保险箱 (Secrets)
进入本仓库的 `Settings -> Secrets and variables -> Actions`，点击 `New repository secret`，依次录入以下加密变量：

| Secret Name (严格一致) | Value 说明 |
| :--- | :--- |
| `API_ID` | 你的 Telegram 开发者 API ID（纯数字，可去 my.telegram.org 申请） |
| `API_HASH` | 你的 Telegram 开发者 API HASH（一串字母数字混合） |
| `TG_SESSION_B64` | **填入第一步提取出来的那一大串 Base64 乱码文本** |
| `GROUP_IDS` | 目标群组 ID 或机器人用户名。支持 `@supersong_bot` 或数字 ID。多个用英文逗号 `,` 隔开。 |
| `CHECKIN_MESSAGE` | 签到发出的指令内容。例如：`/checkin` 或 `签到` |

### 第三步：生成 GitHub 授权钥匙 (PAT Token)
1. 点击 GitHub 右上角个人头像 -> `Settings` -> 左下角 `Developer settings`。
2. 选择 `Personal access tokens` -> `Tokens (classic)` -> `Generate new token (classic)`。
3. Note 随便填（如 `cf-clock`），Expiration 选择 `No expiration`（永不过期）。
4. **核心权限勾选**：勾选第一大项 **`[x] repo`** 即可，拉到最下方生成，并**立刻复制**保存好以 `ghp_` 开头的钥匙。

### 第四步：部署 Cloudflare Workers 闹钟
1. 登录 Cloudflare 控制台，进入 `Workers & Pages` -> `Create application` -> `Create Worker`，命名为 `tg-checkin-alarm` 并部署。
2. 点击 `Edit code`，清空自带代码，将仓库中的 Cloudflare 定时脚本代码粘贴进去，并点击 `Save and deploy`。
3. 进入该 Worker 的 `Settings -> Variables`（变量），在 `Environment Variables` 中录入以下 3 个环境变量：
   * `GITHUB_TOKEN`：填入刚刚生成的以 `ghp_` 开头的钥匙。
   * `REPO_OWNER`：填入你的 GitHub 用户名。
   * `REPO_NAME`：填入本仓库的名称（`tg-auto-checkin`）。
4. **配置定时触发器 (Cron)**：进入 Worker 的 `Settings -> Triggers`（触发器），添加 `Cron Trigger`。
   * 💡 *提示：Cloudflare 使用 UTC 国际标准时间。若想在北京时间每天 **00:05** 触发，对应的 UTC 时间是前一天的 **16:05**，Cron 表达式应填入：`5 16 * * *`*。

---

## 🧪 方案防封安全机制说明
1. **多目标群组间隔**：Python 脚本在循环向多个群组发送消息时，内置了 `await asyncio.sleep(2)` 机制，防止瞬间高频发信触发电报反垃圾系统。
2. **高级随机时间段建议（可选）**：如果想要完全消除定时痕迹以达成极致防封，可以开启 Cloudflare 代码中的概率摇号（几率触发）机制，使每天的实际触发时间完全随机。

---

## 📜 免责声明
本项目仅用于技术交流与个人自动化研究，请勿用于恶意轰炸或任何违反 Telegram 服务条款的活动。因不当使用导致的账号受限或封禁，作者概不负责。

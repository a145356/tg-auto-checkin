async def main():
    check_env()
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    session_b64 = os.environ['TG_SESSION_B64']
    group_ids = [int(g.strip()) for g in os.environ['GROUP_IDS'].split(',') if g.strip()]
    message = os.environ.get('CHECKIN_MESSAGE', '签到')
    os.makedirs('session', exist_ok=True)
    session_path = 'session/action_session.session'
    try:
        with open(session_path, 'wb') as f:
            f.write(base64.b64decode(session_b64))
    except Exception as e:
        print(f"❌ 还原 Session 失败: {e}")
        sys.exit(1)
    print("🔄 正在连接 Telegram 服务器...")
    client = TelegramClient('session/action_session', api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ 错误: 凭证已失效！请在本地电脑/服务器重新提取。")
        await client.disconnect()
        sys.exit(1)
    print("✅ 成功以个人号身份登录！开始发送消息...")
    for g_id in group_ids:
        try:
            target = await client.get_entity(PeerUser(g_id))
            await client.send_message(target, message)
            print(f"✈️ 成功向机器人 [{g_id}] 发送消息: '{message}'")
        except Exception as e:
            print(f"❌ 向机器人 [{g_id}] 发送失败，原因: {e}")
    print("🔒 任务完成，正在安全断开连接...")
    await client.disconnect()
    print("🏁 容器即将销毁。")

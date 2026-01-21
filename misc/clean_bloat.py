import subprocess

packages = [
    "com.oplus.deepthinker", # ColorOS核心AI平台
    "com.oplus.smartengine", # 系统智能引擎AI
    "com.oplus.aiunit", # AI单元服务
    "com.google.android.apps.work.clouddpc", # 企业设备管理
    "com.google.android.onetimeinitializer", # Google开机向导残留
    "com.oplus.pantanal.ums", # 潘塔纳尔跨端互联
    "com.coloros.ocs.opencapabilityservice", # 跨设备能力服务
    "com.android.chrome", # Chrome浏览器
    "com.google.android.youtube", # YouTube
    "com.google.android.googlequicksearchbox", # Google搜索
    "com.google.android.ondevicepersonalization.services", # 谷歌设备端广告AI
    "com.google.android.federatedcompute", # 谷歌联邦计算AI
    "com.google.android.as", # Android智能服务
    "com.google.ar.core", # 谷歌AR服务
    "com.google.android.as.oss", # Android智能服务开源
    "com.google.android.aicore", # Google AI核心
    "com.android.hotwordenrollment.okgoogle", # OK Google唤醒
    "com.android.hotwordenrollment.xgoogle", # Google语音辅助
    "com.google.android.apps.maps", # 谷歌地图
    "com.google.android.apps.bard", # gemini AI
    "com.google.android.adservices.api", # 谷歌广告API
    "com.google.android.projection.gearhead", # Android Auto
    "com.google.android.apps.tachyon", # Google Meet
    "com.google.android.apps.safetyhub", # 个人安全
    "com.google.android.apps.restore", # Google恢复工具
    "com.google.android.partnersetup", # 合作伙伴设置
    "com.google.android.feedback", # 反馈服务
    "com.google.android.tts", # 文字转语音
    "com.facebook.appmanager", # Facebook应用管理
    "com.facebook.services", # Facebook服务
    "com.facebook.system", # Facebook系统组件
    "com.oplus.obrain", # 系统AI大脑
    "com.oplus.qualityprotect", # 质量保护(上传数据)
    "com.oplus.crashbox", # 崩溃日志收集
    "com.oplus.logkit", # 日志工具
    "com.oplus.onetrace", # 跟踪记录
    "com.oplus.statistics.rom", # ROM统计
    "com.oplus.encryption", # 应用加密服务
    "com.oplus.healthservice", # 健康服务
    "com.coloros.assistantscreen", # 负一屏/速览
    "com.coloros.smartsidebar", # 智能侧边栏
    "com.coloros.childrenspace", # 儿童空间
    "com.coloros.scenemode", # 场景模式
    "com.coloros.ocrscanner", # OCR扫描
    "com.coloros.translate.engine", # 翻译引擎
    "com.coloros.accessibilityassistant", # 无障碍助手
    "com.coloros.floatassistant", # 悬浮球
    "com.oneplus.filemanager", # 一加文件管理
    "com.oneplus.account", # 一加账号
    "com.oneplus.oshare", # 互传分享
    "com.heytap.browser", # 自带浏览器
    "com.heytap.colorfulengine", # 多彩引擎
    "com.heytap.accessory", # 配件服务
    "com.oplus.games", # 游戏中心
    "com.oplus.phonemanager", # 手机管家
    "com.oplus.aod", # 息屏显示
    "com.oplus.lfeh", # 负一屏相关
    "com.oplus.linker", # 系统链接器
    "com.oplus.aimemory", # AI内存优化
    "com.oplus.aiwriter", # AI写作
    "com.oplus.securitykeyboard", # 安全键盘
    "com.oplus.securepay", # 支付保护
    "com.oplus.postmanservice", # 邮差服务
    "com.oplus.vdc", # 虚拟显示控制
    "com.qualcomm.location", # 高通定位服务
    "com.qualcomm.qti.powersavemode", # 高通省电模式
    "com.qualcomm.qti.devicestatisticsservice", # 设备统计服务
    "android.autoinstalls.config.oneplus" # 自动安装配置
    "com.oplus.ambient.livealert" # 环境动态提醒
]

def main():
    print(f"Processing {len(packages)} packages...")
    
    for pkg in packages:
        cmd = ["adb", "shell", "pm", "uninstall", "--user", "0", pkg]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if "Success" in res.stdout:
            print(f"[OK] Uninstalled: {pkg}")
        elif "not installed" in res.stderr or "not installed" in res.stdout:
            pass # Silent skip
        else:
            print(f"[FAIL] Could not uninstall: {pkg}")

    print("\nDone. Please reboot.")

if __name__ == "__main__":
    main()
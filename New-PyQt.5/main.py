import sys
import requests
import markdown
import certifi
import os
import traceback
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QRadioButton,
    QCheckBox, QTextEdit, QStackedWidget, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap


class EndlessPixelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EndlessPixel App")
        self.resize(1223, 816)

        # 存储 release 数据: {tag_name: release_dict}
        self.releases = {}

        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === 顶部标题栏 ===
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)

        # === 导航按钮 ===
        nav_layout = QHBoxLayout()
        self.btn_game = QPushButton("游戏")
        self.btn_download = QPushButton("下载")
        self.btn_setting = QPushButton("设置")

        for btn in [self.btn_game, self.btn_download, self.btn_setting]:
            btn.setFixedWidth(100)
            btn.setStyleSheet("font-weight: bold; padding: 5px;")

        self.btn_game.clicked.connect(lambda: self.switch_page(0))
        self.btn_download.clicked.connect(lambda: self.switch_page(1))
        self.btn_setting.clicked.connect(lambda: self.switch_page(2))

        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_game)
        nav_layout.addWidget(self.btn_download)
        nav_layout.addWidget(self.btn_setting)
        nav_layout.addStretch()

        main_layout.addLayout(nav_layout)

        # === 页面堆栈 ===
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # 添加页面
        self.page_game = self.create_game_page()
        self.page_download = self.create_download_page()
        self.page_setting = self.create_setting_page()

        self.stacked_widget.addWidget(self.page_game)
        self.stacked_widget.addWidget(self.page_download)
        self.stacked_widget.addWidget(self.page_setting)

        # 默认显示游戏页
        self.switch_page(0)

        # 底部版权
        footer = QLabel("(C) 2024~2025 EndlessPixel Studio. All rights reserved.          EndlessPixel v1.0.2")
        footer.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(footer)

        # 启动后加载 releases
        self.load_releases()

    def create_title_bar(self):
        frame = QFrame()
        frame.setFixedHeight(80)
        frame.setStyleSheet("background-color: #0080ff;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(40, 20, 40, 20)

        icon_label = QLabel()
        # 如果你有 pAHvtKS.png，取消注释下一行：
        # icon_label.setPixmap(QPixmap("pAHvtKS.png").scaled(40, 40, Qt.KeepAspectRatio))
        layout.addWidget(icon_label)

        title = QLabel("EndlessPixel App")
        title.setFont(QFont("等线", 36, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        layout.addStretch()
        return frame

    def create_game_page(self):
        widget = QWidget()
        layout = QGridLayout(widget)

        layout.addWidget(QLabel("玩家名称"), 0, 0, Qt.AlignRight)
        self.entry_player = QLineEdit()
        layout.addWidget(self.entry_player, 0, 1)

        btn_start = QPushButton("启动")
        btn_instance_manage = QPushButton("实例管理")
        btn_select_instance = QPushButton("选择实例")

        layout.addWidget(btn_select_instance, 1, 0)
        layout.addWidget(btn_instance_manage, 1, 1)
        layout.addWidget(btn_start, 1, 2)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        return widget

    def create_download_page(self):
        widget = QWidget()
        layout = QGridLayout(widget)

        layout.addWidget(QLabel("你要安装哪个版本的 EndlessPixel ModPack？"), 0, 0)
        self.combo_version = QComboBox()
        layout.addWidget(self.combo_version, 0, 1)

        btn_install = QPushButton("开始安装")
        layout.addWidget(btn_install, 0, 2)

        layout.addWidget(QLabel("版本更新日志"), 1, 0)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setAcceptRichText(True)  # 支持 HTML
        layout.addWidget(self.log_text, 2, 0, 1, 3)

        radio_modrinth = QRadioButton("Modrinth安装模式")
        btn_issues = QPushButton("查看 issues")
        layout.addWidget(radio_modrinth, 1, 1)
        layout.addWidget(btn_issues, 1, 2)

        # 连接信号
        self.combo_version.currentIndexChanged.connect(self.on_version_changed)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        return widget

    def create_setting_page(self):
        widget = QWidget()
        layout = QGridLayout(widget)

        layout.addWidget(QLabel("分配内存大小（mb）"), 0, 0, Qt.AlignLeft)
        self.mem_entry = QLineEdit("4096")
        layout.addWidget(self.mem_entry, 0, 1)

        layout.addWidget(QLabel("进程优先级"), 1, 0, Qt.AlignLeft)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["极低", "低", "中等", "较高", "高"])
        layout.addWidget(self.priority_combo, 1, 1)

        layout.addWidget(QLabel("版本隔离"), 2, 0, Qt.AlignLeft)
        self.isolation_combo = QComboBox()
        self.isolation_combo.addItems([
            "不隔离", "开启", "仅隔离可安装mod版本",
            "隔离非正式版", "可安装mod版本和非正式版"
        ])
        layout.addWidget(self.isolation_combo, 2, 1)

        layout.addWidget(QLabel("游戏Java"), 3, 0, Qt.AlignLeft)
        self.java_entry = QLineEdit()
        layout.addWidget(self.java_entry, 3, 1)

        layout.addWidget(QLabel("Java虚拟机参数"), 4, 0, Qt.AlignLeft)
        self.jvm_entry = QLineEdit(
            "-XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow "
            "-Djdk.lang.Process.allowAmbiguousCommands=true -Dfml.ignoreInvalidMinecraftCertificates=True "
            "-Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true"
        )
        layout.addWidget(self.jvm_entry, 4, 1, 1, 2)

        layout.addWidget(QLabel("下载方式"), 5, 0, Qt.AlignLeft)
        self.download_mode = QComboBox()
        self.download_mode.addItems([
            "尽量使用镜像源",
            "优先使用官方源，在加载缓慢时换用镜像源",
            "尽量使用官方源"
        ])
        layout.addWidget(self.download_mode, 5, 1)

        layout.addWidget(QLabel("最大线程数"), 6, 0, Qt.AlignLeft)
        self.thread_entry = QLineEdit("64")
        layout.addWidget(self.thread_entry, 6, 1)

        layout.addWidget(QLabel("速度限制（kb/s）"), 7, 0, Qt.AlignLeft)
        self.speed_entry = QLineEdit("2048")
        layout.addWidget(self.speed_entry, 7, 1)

        layout.addWidget(QLabel("目标文件夹"), 8, 0, Qt.AlignLeft)
        self.folder_entry = QLineEdit("./.minecraft/")
        layout.addWidget(self.folder_entry, 8, 1)

        layout.addWidget(QLabel("游戏参数"), 9, 0, Qt.AlignLeft)
        self.game_args = QLineEdit()
        layout.addWidget(self.game_args, 9, 1)

        layout.addWidget(QLabel("启动前执行命令"), 10, 0, Qt.AlignLeft)
        self.pre_cmd = QLineEdit()
        layout.addWidget(self.pre_cmd, 10, 1)

        layout.addWidget(QLabel("离线皮肤   (由于技术问题，此功能只保证对1.19.2 以前的版本有效！)"), 11, 0, 1, 2)

        skin_layout = QHBoxLayout()
        self.skin_random = QRadioButton("随机")
        self.skin_steve = QRadioButton("Steve")
        self.skin_alex = QRadioButton("Alex")
        self.skin_official = QRadioButton("正版皮肤")
        self.skin_user = QLineEdit()
        self.skin_user.setPlaceholderText("输入用户名")

        skin_layout.addWidget(self.skin_random)
        skin_layout.addWidget(self.skin_steve)
        skin_layout.addWidget(self.skin_alex)
        skin_layout.addWidget(self.skin_official)
        skin_layout.addWidget(self.skin_user)
        layout.addLayout(skin_layout, 12, 0, 1, 2)

        check_layout = QHBoxLayout()
        self.chk_gpu = QCheckBox("要求Java 使用高性能显卡")
        self.chk_no_wrapper = QCheckBox("禁用 Java Launch Wrapper")
        self.chk_no_update = QCheckBox("禁止更新Mod")
        check_layout.addWidget(self.chk_gpu)
        check_layout.addWidget(self.chk_no_wrapper)
        check_layout.addWidget(self.chk_no_update)
        layout.addLayout(check_layout, 13, 0, 1, 2)

        check_layout2 = QHBoxLayout()
        self.chk_ssl = QCheckBox("在正版登录时验证SSL证书")
        self.chk_chinese = QCheckBox("游戏语言自动设置为中文")
        self.chk_optimize = QCheckBox("启动游戏前进行内存优化")
        check_layout2.addWidget(self.chk_ssl)
        check_layout2.addWidget(self.chk_chinese)
        check_layout2.addWidget(self.chk_optimize)
        layout.addLayout(check_layout2, 14, 0, 1, 2)

        check_layout3 = QHBoxLayout()
        self.chk_no_verify = QCheckBox("关闭文件校验")
        self.chk_ignore_java = QCheckBox("忽略Java 兼容性警告")
        check_layout3.addWidget(self.chk_no_verify)
        check_layout3.addWidget(self.chk_ignore_java)
        layout.addLayout(check_layout3, 15, 0, 1, 2)

        layout.setColumnStretch(1, 1)
        return widget

    def load_releases(self):
        """从 GitHub API 获取 releases 并填充下拉框，使用 certifi 解决 SSL 问题"""
        url = "https://api.github.com/repos/EndlessPixel/EndlessPixel-Modpack/releases"
        cert_path = certifi.where()
        if not os.path.exists(cert_path):
            self.log_text.setPlainText(
                f"❌ 找不到 certifi 的 CA 文件:\n{cert_path}\n\n请运行 `pip install certifi`，或将环境变量 `SSL_CERT_FILE` 指向正确的 CA 文件，然后重启应用。"
            )
            return
        try:
            # 允许用户通过设置禁用证书校验（不安全）
            verify = cert_path if not getattr(self, 'chk_no_verify', None) or not self.chk_no_verify.isChecked() else False
            response = requests.get(url, timeout=10, verify=verify)
            response.raise_for_status()
            data = response.json()

            self.releases.clear()
            self.combo_version.clear()

            for release in data:
                tag = release["tag_name"]
                name = release.get("name", tag)
                body = release.get("body", "")
                self.releases[tag] = {
                    "name": name,
                    "body": body
                }
                self.combo_version.addItem(f"{name} ({tag})", tag)

            if self.releases:
                self.combo_version.setCurrentIndex(0)
                self.on_version_changed(0)

        except requests.exceptions.SSLError:
            tb = traceback.format_exc()
            msg = (
                "❌ SSL 验证失败: 无法验证 GitHub 的 TLS 证书。\n\n"
                "可能原因：\n"
                "- 本机缺少根证书（certifi 未正确安装或 CA 文件丢失）\n"
                "- 公司/校园网络的 HTTPS 检查（中间人）使用了未被信任的 CA\n\n"
                "建议：\n"
                "1) 在终端运行：\n"
                "   python -c \"import certifi, os; print(certifi.where(), os.path.exists(certifi.where()))\"\n"
                "2) 若你在公司网络，请向 IT 获取内部 CA 证书并将其追加到 certifi 的 CA 文件，或生成一个合并后的 PEM 文件并设置环境变量：\n"
                "   setx REQUESTS_CA_BUNDLE \"C:\\path\\to\\combined-ca.pem\" -m\n"
                "   或 setx SSL_CERT_FILE \"C:\\path\\to\\combined-ca.pem\" -m\n"
                "3) 临时方案（不安全）：在设置中勾选“关闭文件校验”并重试（仅在你理解风险时使用）。\n\n详细错误信息：\n"
                + tb
            )
            self.log_text.setPlainText(msg)
        except Exception:
            tb = traceback.format_exc()
            self.log_text.setPlainText(f"❌ 无法加载版本列表:\n{tb}")

    @pyqtSlot(int)
    def on_version_changed(self, index):
        """当下拉框切换时，更新日志"""
        if index < 0:
            return
        tag = self.combo_version.itemData(index)
        if tag in self.releases:
            md_content = self.releases[tag]["body"]
            html = markdown.markdown(
                md_content or "*暂无更新日志*",
                extensions=['fenced_code', 'tables', 'nl2br']
            )
            self.log_text.setHtml(html)
        else:
            self.log_text.setPlainText("未找到该版本的日志。")

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.btn_game.setEnabled(index != 0)
        self.btn_download.setEnabled(index != 1)
        self.btn_setting.setEnabled(index != 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EndlessPixelApp()
    window.show()
    sys.exit(app.exec_())
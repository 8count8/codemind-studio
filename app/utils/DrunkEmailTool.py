"""
DrunkEmailTool.py

作者: Drunk
日期: 2024年10月

描述:
    该文件是一个用于处理邮件发送的工具。它支持通过网易邮箱的SMTP服务器发送邮件。
    包含以下功能:
    - 支持JSON或.env文件存储配置
    - 配置文件的创建和读取
    - 邮件配置的验证
    - 邮件内容的构建和发送

使用说明:
    1. 确保已安装所需的Python库: json, os, smtplib, ssl, email.mime.multipart, email.mime.text, re
    2. 使用.env配置时需要安装python-dotenv: pip install python-dotenv
    3. 运行脚本时，如果配置文件不存在会提示创建
    4. 使用EmailConfig类配置邮件信息
    5. 使用EmailTool类发送邮件

示例:
    # 使用默认JSON配置
    email_tool = EmailTool()

    # 使用.env配置
    email_tool = EmailTool(storage_type='env')

    email_tool.set_message("测试邮件", "这是一封测试邮件", ContentType.TEXT)
    email_tool.send("receiver@example.com")
"""
import json
import os
import smtplib
from enum import Enum
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re


# 定义邮件类型枚举类
class EmailType(Enum):
    NETEASE_EMAIL_SMTP_SSL = 'NETEASE_EMAIL_SMTP_SSL'


# 定义邮件内容类型枚举类
class ContentType(Enum):
    TEXT = 'text'  # 文本
    HTML = 'html'  # HTML
    PLAIN = 'plain'  # 纯文本


# 网易邮箱SMTP服务器地址和SSL端口
NETEASE_EMAIL_SMTP_HOST = 'smtp.163.com'
NETEASE_EMAIL_SMTP_SSL_PORT = 465

# JSON配置文件路径
JSON_CONFIG_FILE = '../EmailToolConfig.json'


def validate_email(email):
    """验证邮箱地址格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def check_and_create_json_config():
    """检查并创建JSON配置文件"""
    try:
        if not os.path.exists(JSON_CONFIG_FILE):
            print("JSON配置文件不存在，正在创建...")

            email_type_input = input("请选择服务邮箱类型(输入序号)：\n\t1.163网易邮箱\n>> ")
            address = input("请输入您的服务邮箱地址：")
            password = input("请输入您的授权码：")
            receivers_input = input("请输入接收者邮箱地址列表，多个地址用英文逗号分隔（若没有则输入数字0）：")

            # 处理接收者列表
            receivers = [r.strip() for r in receivers_input.split(',')]
            if len(receivers) == 1 and receivers[0] == '0':
                receivers = []

            # 设置email_type
            if email_type_input == '1':
                email_type = EmailType.NETEASE_EMAIL_SMTP_SSL
            else:
                raise ValueError("无效的服务邮箱类型选择")

            with open(JSON_CONFIG_FILE, 'w') as f:
                json.dump({
                    "email_type": email_type.name,
                    "address": address,
                    "password": password,
                    "receivers": receivers
                }, f)
            print("JSON配置文件已创建")
    except Exception as e:
        print(f"处理JSON配置文件时出错: {e}")
        if isinstance(e, ValueError):
            check_and_create_json_config()


def read_json_config():
    """读取JSON配置文件"""
    check_and_create_json_config()
    with open(JSON_CONFIG_FILE, 'r') as f:
        return json.load(f)


def check_and_create_env_config():
    """检查并创建.env配置文件"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        required_vars = ['EMAIL_TYPE', 'EMAIL_ADDRESS', 'EMAIL_PASSWORD']
        if not all(os.getenv(var) for var in required_vars):
            print(".env配置不完整，正在创建...")

            email_type_input = input("请选择服务邮箱类型(输入序号)：\n\t1.163网易邮箱\n>> ")
            address = input("请输入您的服务邮箱地址：")
            password = input("请输入您的授权码：")
            receivers_input = input("请输入接收者邮箱地址列表，多个地址用英文逗号分隔（若没有则输入数字0）：")

            # 处理接收者信息
            receivers = [r.strip() for r in receivers_input.split(',')]
            if len(receivers) == 1 and receivers[0] == '0':
                receivers = []

            # 转换邮箱类型
            email_type = EmailType.NETEASE_EMAIL_SMTP_SSL.name if email_type_input == '1' else ''

            with open('.env', 'w') as f:
                f.write(f"EMAIL_TYPE={email_type}\n")
                f.write(f"EMAIL_ADDRESS={address}\n")
                f.write(f"EMAIL_PASSWORD={password}\n")
                f.write(f"EMAIL_RECEIVERS={','.join(receivers) if receivers else ''}\n")
            print(".env配置文件已创建")
    except ImportError:
        raise ImportError("使用.env配置需要安装python-dotenv，请执行: pip install python-dotenv")
    except Exception as e:
        print(f"处理.env配置文件时出错: {e}")
        if isinstance(e, ValueError):
            check_and_create_env_config()


def read_env_config():
    """读取环境变量配置 (支持 .env 文件和系统环境变量)"""
    # 优先尝试加载 .env 文件（仅本地开发使用）
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)  # 不覆盖已存在的环境变量
    except ImportError:
        pass

    email_type = os.getenv('EMAIL_TYPE', '')
    email_address = os.getenv('EMAIL_ADDRESS', '')
    email_password = os.getenv('EMAIL_PASSWORD', '')
    receivers_str = os.getenv('EMAIL_RECEIVERS', '')

    print(f"[EMAIL] 环境变量检查: EMAIL_TYPE={'SET' if email_type else 'MISSING'}, "
          f"EMAIL_ADDRESS={'SET' if email_address else 'MISSING'}, "
          f"EMAIL_PASSWORD={'SET' if email_password else 'MISSING'}")

    return {
        "email_type": email_type,
        "address": email_address,
        "password": email_password,
        "receivers": [r.strip() for r in receivers_str.split(',')] if receivers_str else []
    }


class EmailConfig:
    def __init__(self, storage_type='json'):
        """
        邮件配置类
        :param storage_type: 配置存储类型，可选'json'或'env'
        """
        if storage_type == 'json':
            config = read_json_config()
        elif storage_type == 'env':
            config = read_env_config()
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")

        self.email_type = config.get('email_type', '')
        self.address = config.get('address', '')
        self.password = config.get('password', '')
        self.receivers = config.get('receivers', [])

        # 延迟转换 EmailType，允许 None 以支持更早的错误诊断
        if self.email_type:
            try:
                self.email_type = EmailType[self.email_type]
            except KeyError:
                print(f"[EMAIL] 未知的邮件类型: {self.email_type}")

    def validate(self):
        """验证配置有效性"""
        if not self.email_type or not isinstance(self.email_type, EmailType):
            raise ValueError("邮件类型未配置或无效")
        if not self.address or not validate_email(self.address):
            raise ValueError("发送者邮箱地址无效")
        if not self.password:
            raise ValueError("授权码不能为空")


class Email:
    def __init__(self):
        self.address = None  # 发送者
        self.receivers = None  # 接收者
        self.content = None  # 邮件内容
        self.subject = None  # 邮件主题

    def to_email_message(self):
        message = MIMEMultipart()
        message['Subject'] = self.subject
        message['From'] = self.address
        message['To'] = ', '.join(self.receivers) if isinstance(self.receivers, list) else self.receivers
        message.attach(self.content)
        return message


class EmailTool:
    def __init__(self, storage_type='json'):
        """
        邮件工具类
        :param storage_type: 配置存储类型，可选'json'或'env'，默认为json
        """
        self.config = EmailConfig(storage_type)
        self.config.validate()

        self.email = Email()
        self.email_server_port = None
        self.email_server_host = None
        self.configure_server()
        self.configure_email()
        self.email_password = self.config.password

    def configure_server(self):
        """配置邮件服务器"""
        if self.config.email_type == EmailType.NETEASE_EMAIL_SMTP_SSL:
            self.email_server_host = NETEASE_EMAIL_SMTP_HOST
            self.email_server_port = NETEASE_EMAIL_SMTP_SSL_PORT
        else:
            raise ValueError("不支持的邮件类型")

    def configure_email(self):
        """初始化邮件基础配置"""
        self.email.address = self.config.address
        self.email.receivers = self.config.receivers


    def set_message(self, subject, content, content_type=ContentType.TEXT):
        if not subject or not content:
            raise ValueError("邮件主题和内容不能为空")

        if content_type == ContentType.TEXT or content_type == ContentType.PLAIN:
            self.email.content = MIMEText(content, 'plain', 'utf-8')
        elif content_type == ContentType.HTML:
            self.email.content = MIMEText(content, 'html', 'utf-8')
        else:
            raise ValueError("无效的邮件内容类型")

        self.email.subject = subject

    def set_address(self, address: str):
        if not validate_email(address):
            raise ValueError("无效的发送者邮箱地址")
        self.email.address = address

    def set_receivers(self, receivers):
        if not receivers:
            raise ValueError("无效的接收者邮箱地址列表")
        self.email.receivers = receivers

    def set_password(self, password: str):
        if not password:
            raise ValueError("授权码不能为空")
        self.email_password = password

    def sends(self, receivers=None):
        if not self.email.address:
            raise ValueError("发送者邮箱地址必须设置")
        if not self.email_password:
            raise ValueError("授权码必须设置")
        if receivers:
            self.email.receivers = receivers

        # 创建SSL上下文
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self.email_server_host, self.email_server_port, context=context) as smtp:
                smtp.login(self.email.address, self.email_password)
                smtp.send_message(self.email.to_email_message())
        except smtplib.SMTPException as e:
            print(f"邮件发送失败: {e}")
        except Exception as e:
            print(f"未知错误: {e}")

    def send(self, receiver: str):
        if not self.email.address or not self.config.password:
            print(f"[EMAIL] 配置缺失: address={self.email.address}, password={'***' if self.config.password else 'MISSING'}")
            raise ValueError("发送者邮箱地址和授权码必须设置")

        print(f"[EMAIL] 正在连接 SMTP 服务器: {self.email_server_host}:{self.email_server_port}")
        print(f"[EMAIL] 登录账号: {self.email.address}")
        print(f"[EMAIL] 发送至: {receiver}")

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self.email_server_host, self.email_server_port, context=context, timeout=30) as smtp:
                smtp.login(self.email.address, self.email_password)
                self.set_receivers(receiver)
                smtp.send_message(self.email.to_email_message())
                print(f"[EMAIL] 邮件发送成功: {receiver}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL] SMTP 认证失败: {e}")
            raise Exception("SMTP 认证失败，请检查邮箱账号和授权码")
        except smtplib.SMTPRecipientsRefused as e:
            print(f"[EMAIL] 收件人被拒绝: {e}")
            raise Exception("收件人地址无效或被拒绝")
        except smtplib.SMTPException as e:
            print(f"[EMAIL] SMTP 错误: {type(e).__name__}: {e}")
            raise Exception(f"SMTP 错误: {e}")
        except Exception as e:
            print(f"[EMAIL] 未知错误: {type(e).__name__}: {e}")
            raise Exception(f"邮件发送失败: {e}")


# 示例用法
if __name__ == "__main__":
    email_tool = EmailTool("env")
    email_tool.set_message("测试邮件", "这是一封测试邮件(来自:CMS)", ContentType.TEXT)
    email_tool.send("3202731886@qq.com")

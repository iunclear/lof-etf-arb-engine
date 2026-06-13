import os
import sys
import time
import socket

# Ensure LOFarb directory is in sys.path so we can find account_private.py when imported from elsewhere
_tm_dir = os.path.dirname(os.path.abspath(__file__))
_lof_dir = os.path.normpath(os.path.join(_tm_dir, "..", "..", "LOFarb"))
if os.path.exists(_lof_dir) and _lof_dir not in sys.path:
    sys.path.append(_lof_dir)

# 导入本地敏感配置
try:
    from account_private import GJS_ACCOUNT
except ImportError:
    GJS_ACCOUNT = os.getenv('GJS_ACCOUNT')
    if not GJS_ACCOUNT:
        print("INFO: 未找到 account_private.py 且未配置 GJS_ACCOUNT，通达信交易功能将保持禁用")

class TradeManager:
    """A股/LOF统一交易接口管理器"""
    def __init__(self):
        self.tdx_available = False
        self.tq = None
        self.tdx_account = GJS_ACCOUNT

        # self.xtquant_available = False  # 国金QMT已注释，用户不使用
        # self.xt_trader = None
        # self.xt_account = None
        # self.xtconstant = None

        # 启动时自动初始化可用通道
        self._init_tdx()
        # self._init_guojin_qmt()  # 国金QMT已注释

    def _init_tdx(self):
        try:
            # 仅使用新版 tqcenter 路径
            tdx_api_path = os.getenv('TDX_PLUGIN_DIR', r'C:\new_tdx64\PYPlugins\user')

            sys.path_importer_cache.clear()
            if 'tqcenter' in sys.modules:
                del sys.modules['tqcenter']

            if os.path.exists(tdx_api_path) and tdx_api_path not in sys.path:
                sys.path.insert(0, tdx_api_path)

            from tqcenter import tq
            self.tq = tq

            tdx_plugin_path = os.path.join(tdx_api_path, 'tqcenter.py')
            tq.initialize(tdx_plugin_path)

            if self.tdx_account:
                self.tdx_available = True
                print(f"SUCCESS: [TradeManager] 已挂载【通达信】交易通道 (账号配置已加载)")
            else:
                print("WARNING: [TradeManager] tqcenter 已初始化，但缺少 GJS_ACCOUNT 账号配置，交易功能不可用")

        except ImportError as e:
            print(f"INFO: [TradeManager] 未检测到新版通达信环境(tqcenter): {e}")
        except Exception as e:
            print(f"INFO: [TradeManager] 通达信模块跳过加载: {e}")

    # 【国金QMT已注释】用户不使用
    # def _init_guojin_qmt(self):
    #     try:
    #         # ====================== 国金 QMT 路径与环境配置 ======================
    #         QMT_INSTALL_PATH = r"D:\GJQMT"
    #         if os.path.exists(QMT_INSTALL_PATH):
    #             if QMT_INSTALL_PATH not in sys.path:
    #                 sys.path.append(QMT_INSTALL_PATH)
    #                 sys.path.append(os.path.join(QMT_INSTALL_PATH, "lib"))
    #                 sys.path.append(os.path.join(QMT_INSTALL_PATH, "bin.x64"))
    #                 sys.path.append(os.path.join(QMT_INSTALL_PATH, "bin.x64", "Lib", "site-packages"))
    #             
    #             from xtquant import xttrader, xtconstant
    #             from xtquant.xttype import StockAccount
    #             
    #             qmt_path = os.path.join(QMT_INSTALL_PATH, 'userdata_mini')
    #             session_id = int(time.time())
    #             self.xt_trader = xttrader.XtQuantTrader(qmt_path, session_id)
    #             self.xt_account = StockAccount(GJS_ACCOUNT)
    #             self.xtconstant = xtconstant
    #             
    #             self.xt_trader.start()
    #             connect_result = self.xt_trader.connect()
    #             if connect_result == 0:
    #                 self.xt_trader.subscribe(self.xt_account)
    #                 self.xtquant_available = True
    #                 print(f"✅ SUCCESS: [TradeManager] 已挂载【国金MiniQMT】原生直连通道 (账号:{self.xt_account.account_id})")
    #             else:
    #                 print(f"WARNING: [TradeManager] 国金QMT客户端连接失败 (错误码: {connect_result})")
    #     except Exception as e:
    #         print(f"INFO: [TradeManager] 国金QMT模块跳过加载: {e}")

    def send_order(self, broker, action, symbol, volume, price):
        """暴露给外部的统一路由函数"""
        if broker == 'yinhe_qmt':
            try:
                cmd_str = f"{action},{symbol},{volume},{price}\n"
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(2.0)
                client.connect((os.getenv('GALAXY_QMT_HOST', '127.0.0.1'), int(os.getenv('GALAXY_QMT_PORT', '8888'))))
                client.sendall(cmd_str.encode('utf-8'))
                # 只取第一行（订单确认），忽略后续TICK广播数据
                raw_response = client.recv(4096).decode('utf-8')
                client.close()
                first_line = raw_response.split('\n')[0].strip()
                if first_line == 'OK':
                    return True, f"银河QMT下单成功"
                else:
                    return True, f"银河QMT返回: {first_line}"
            except ConnectionRefusedError:
                return False, "银河QMT未开启或 8888 桥接策略未运行"
            except Exception as e:
                return False, f"银河QMT下单异常: {str(e)}"
                
        elif broker == 'guojin_qmt':
            return False, "国金QMT已禁用"  # 【国金QMT已注释】用户不使用
                
        elif broker == 'tdx':
            if not self.tdx_available: return False, "通达信接口未就绪或缺少账号配置"
            try:
                order_type = 0 if action == 'BUY' else 1
                price_type = 0

                result = self.tq.order_stock(
                    account=self.tdx_account,
                    stock_code=symbol,
                    order_type=order_type,
                    order_volume=int(volume),
                    price_type=price_type,
                    price=float(price),
                    strategy_name="ArbDashboard",
                    order_remark=""
                )

                if not isinstance(result, dict):
                    return False, f"通达信下单失败: {result}"

                error_id = str(result.get('ErrorId', result.get('ErrorID', -1)))
                msg = result.get('Msg') or result.get('Error') or result.get('Message') or '未知'

                if error_id == '0':
                    wtbh = result.get('Wtbh') or result.get('OrderID') or result.get('Value') or ''
                    return True, f"通达信下单成功，委托编号: {wtbh}"
                else:
                    return False, f"通达信下单失败: {msg}"

            except Exception as e:
                return False, f"通达信下单异常: {str(e)}"
                
        return False, f"未知的通道标识: {broker}"
# 导入函数库
from jqdata import *

# 初始化函数，设定基准等等
def initialize(context):
    # 设定基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    
    ### 账户相关设定 ###
    # 设置账户类型
    set_subportfolios([SubPortfolioConfig(cash=context.portfolio.cash, type='stock_margin')])
    
    # --- 策略参数 ---
    # 监控的特定营业部模式
    g.target_seat_patterns = [
        '特定营业部模式1',
        '特定营业部模式2',
        '特定营业部模式3',
        '特定营业部模式4'
    ]
    
    # 灵活的关键词组合
    g.target_keywords = {
        '模式1': ['模式1', '变体1', '特征1'],
        '模式2': ['模式2', '变体2', '特征2'], 
        '模式3': ['模式3', '变体3', '特征3'],
        '模式4': ['模式4', '变体4', '特征4']
    }
    
    # 策略核心参数
    g.holding_days = 5
    g.max_position_ratio = 0.1
    g.max_daily_ratio = 0.8
    g.stop_loss_rate = 0.08
    g.stop_profit_rate = 0.15
    g.positions_info = {}
    
    # 定时运行函数
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    run_daily(market_open, time='open', reference_security='000300.XSHG')
    run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')

def before_market_open(context):
    """开盘前运行"""
    g.previous_date = context.previous_date

def market_open(context):
    """开盘时运行"""
    check_close_positions(context)
    open_new_positions(context)

def after_market_close(context):
    """收盘后运行"""
    log.info('策略当日运行完成')

def check_close_positions(context):
    """检查并处理需要平仓的股票 - 框架逻辑"""
    current_date = context.current_dt.date()
    
    # 获取当前持仓
    current_positions = get_current_positions(context)
    
    for stock in list(current_positions.keys()):
        position_info = g.positions_info.get(stock, {})
        if not position_info:
            continue
            
        current_price = get_current_price(stock)
        if current_price is None:
            continue
            
        open_price = position_info.get('price', 0)
        open_date = position_info.get('date', current_date)
        
        # 计算持有天数
        holding_days = (current_date - open_date).days
        
        # 平仓条件判断
        close_reason = None
        
        # 条件1: 达到持仓周期
        if holding_days >= g.holding_days:
            close_reason = "持仓周期到期"
        
        # 条件2: 止损检查
        elif current_price >= open_price * (1 + g.stop_loss_rate):
            close_reason = "触发止损"
            
        # 条件3: 止盈检查  
        elif current_price <= open_price * (1 - g.stop_profit_rate):
            close_reason = "触发止盈"
        
        # 执行平仓
        if close_reason:
            execute_close_position(context, stock, current_price, close_reason)

def open_new_positions(context):
    """开立新的仓位 - 框架逻辑"""
    # 1. 获取目标股票
    target_stocks = get_target_stocks_from_billboard(context)
    
    if not target_stocks:
        log.info("当日无符合条件的目标股票")
        return
        
    # 2. 过滤已持仓股票
    current_positions = set(get_current_positions(context).keys())
    target_stocks = [stock for stock in target_stocks if stock not in current_positions]
    
    if not target_stocks:
        log.info("所有目标股票均已持仓")
        return
        
    # 3. 计算仓位
    available_cash = context.portfolio.cash
    max_daily_cash = context.portfolio.total_value * g.max_daily_ratio
    cash_to_use = min(available_cash, max_daily_cash)
    
    position_value_per_stock = min(
        cash_to_use / len(target_stocks),
        context.portfolio.total_value * g.max_position_ratio
    )
    
    # 4. 执行开仓
    for stock in target_stocks:
        if position_value_per_stock <= 0:
            break
            
        current_price = get_current_price(stock)
        if current_price is None or current_price <= 0:
            continue
            
        # 执行开仓操作
        if execute_open_position(context, stock, current_price, position_value_per_stock):
            g.positions_info[stock] = {
                'price': current_price,
                'date': context.current_dt.date()
            }

def get_target_stocks_from_billboard(context):
    """从市场数据中获取目标股票 - 核心逻辑框架"""
    target_stocks = []
    
    try:
        # 获取市场数据
        market_data = get_market_data(context)
        
        if not market_data:
            log.info("前一日无相关市场数据")
            return target_stocks
        
        log.info(f"前一日共有 {len(market_data)} 条市场记录")
        
        # 筛选符合条件的记录
        filtered_records = filter_target_records(market_data)
        
        log.info(f"符合条件记录: {len(filtered_records)} 条")
        
        if len(filtered_records) > 0:
            # 按股票代码分组分析
            stock_analysis = analyze_stock_groups(filtered_records)
            
            for stock_code, analysis_data in stock_analysis.items():
                total_buy_value = analysis_data['total_value']
                buy_ratio = analysis_data['ratio']
                seats_info = analysis_data['seats_info']
                
                log.info(f"分析股票: {stock_code}, 买入金额: {total_buy_value:.2f}, 占比: {buy_ratio:.2%}")
                
                # 添加筛选条件
                if meets_strategy_criteria(analysis_data):
                    target_stocks.append(stock_code)
                    log.info(f"符合策略条件，加入目标列表: {stock_code}")
                else:
                    log.info(f"不符合策略条件，过滤: {stock_code}")
                
    except Exception as e:
        log.error(f"获取或处理市场数据出错: {e}")
        import traceback
        log.error(traceback.format_exc())
        
    return target_stocks

def get_market_data(context):
    """获取市场数据 - 需要根据实际情况实现"""
    # 这里返回模拟数据或实际市场数据
    # 在实际使用中，这里可以接入各种市场数据源
    return []

def filter_target_records(market_data):
    """筛选目标记录 - 核心筛选逻辑"""
    filtered_records = []
    
    for record in market_data:
        if is_target_pattern(record):
            filtered_records.append(record)
    
    return filtered_records

def is_target_pattern(record):
    """判断是否符合目标模式 - 核心识别逻辑"""
    # 这里实现你的模式识别逻辑
    # 可以基于营业部名称、交易行为等特征
    
    # 示例：基于特定关键词的模式识别
    depart_name = record.get('sales_depart_name', '')
    if not depart_name:
        return False
        
    # 方法1: 子串匹配
    for pattern in g.target_seat_patterns:
        if pattern in depart_name:
            return True
    
    # 方法2: 关键词组合匹配
    if contains_target_keywords(depart_name):
        return True
        
    # 方法3: 正则表达式匹配
    if match_target_by_regex(depart_name):
        return True
        
    return False

def contains_target_keywords(depart_name):
    """使用关键词组合匹配目标模式"""
    depart_name = depart_name.lower()
    
    # 必须包含核心关键词
    if '核心特征' not in depart_name:
        return False
        
    # 检查其他特征
    keywords_to_check = ['特征1', '特征2', '特征3']
    for keyword in keywords_to_check:
        if keyword in depart_name:
            return True
            
    return False

def match_target_by_regex(depart_name):
    """使用正则表达式匹配目标模式"""
    import re
    
    patterns = [
        r'核心特征.*模式1.*标识',
        r'核心特征.*模式2.*标识',
        r'核心特征.*模式3.*标识'
    ]
    
    for pattern in patterns:
        if re.search(pattern, depart_name):
            return True
            
    return False

def analyze_stock_groups(filtered_records):
    """分析股票分组数据"""
    stock_analysis = {}
    
    # 按股票代码分组
    groups = {}
    for record in filtered_records:
        stock_code = record.get('code')
        if stock_code not in groups:
            groups[stock_code] = []
        groups[stock_code].append(record)
    
    # 分析每个股票
    for stock_code, records in groups.items():
        total_buy_value = sum(record.get('buy_value', 0) for record in records)
        stock_total_amount = records[0].get('amount', 1) if records else 1
        buy_ratio = total_buy_value / stock_total_amount if stock_total_amount > 0 else 0
        
        # 收集席位信息
        seats = [f"{record.get('sales_depart_name', '')}" for record in records]
        seats_info = ', '.join(set(seats))
        
        stock_analysis[stock_code] = {
            'total_value': total_buy_value,
            'ratio': buy_ratio,
            'seats_info': seats_info,
            'record_count': len(records)
        }
    
    return stock_analysis

def meets_strategy_criteria(analysis_data):
    """判断是否满足策略条件"""
    total_value = analysis_data['total_value']
    buy_ratio = analysis_data['ratio']
    
    # 示例条件：买入金额大于阈值
    if total_value > 1000000:  # 100万元
        return True
        
    return False

# 以下为工具函数，保持框架但移除具体实现
def get_current_positions(context):
    """获取当前持仓 - 需要根据账户类型实现"""
    return {}

def get_current_price(stock):
    """获取当前价格"""
    try:
        return get_price(stock, count=1, fields='close', skip_paused=True)['close'][0]
    except:
        return None

def execute_open_position(context, stock, price, position_value):
    """执行开仓操作 - 需要根据交易方式实现"""
    log.info(f"执行开仓: {stock}, 价格: {price:.2f}, 金额: {position_value:.2f}")
    # 这里实现具体的开仓逻辑
    return True

def execute_close_position(context, stock, price, reason):
    """执行平仓操作 - 需要根据交易方式实现"""
    log.info(f"执行平仓: {stock}, 价格: {price:.2f}, 原因: {reason}")
    # 这里实现具体的平仓逻辑
    return True
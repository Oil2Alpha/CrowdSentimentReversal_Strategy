# LhasaRetailHunter - 市场微观结构交易策略

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-QuantResearch-brightgreen.svg)]()

## 📖 策略概述

CrowdSentimentReversal是一个基于市场微观结构和行为金融学的量化交易策略。该策略以A股龙虎榜上榜席位和交易量为参考，通过分析特定市场参与者的交易行为模式，识别潜在的短期市场非有效性机会，进行融券做空，获取超额阿尔法收益。策略通过仓位控制和牛熊市识别进行风控。该策略在熊市和波动市表现良好，牛市表现较差。（开源代码中核心选股逻辑已删改，仅供参考）

> 🔒 **注意**: 本仓库包含的是策略框架和核心逻辑，具体的敏感参数和实现细节已做脱敏处理。

## 🧠 策略理念

### 核心思想
基于行为金融学中的"散户情绪指标"，当某些特定模式的零售交易行为出现时，市场可能会出现短期的定价偏差，这为反向交易策略提供了机会。

### 理论基础
- **行为金融学**: 投资者情绪与市场非有效性
- **市场微观结构**: 订单流分析与参与者行为识别
- **逆向投资**: 与特定市场情绪反向操作

## ⚙️ 策略特性

### 🎯 目标识别
- 多模式匹配算法识别特定交易行为
- 基于正则表达式的灵活模式匹配
- 多层次过滤确保信号质量

### 📊 风险管理
- 动态仓位控制
- 多条件止损止盈机制
- 持仓周期限制

### 🔄 交易逻辑
- 数据获取 → 模式识别 → 风险评估 → 仓位管理 → 绩效监控

## 🏗️ 策略框架

### 核心模块

#### 1. 数据层 (Data Layer)
get_market_data()          # 市场数据获取
filter_target_records()    # 目标记录筛选
analyze_stock_groups()     # 股票分组分析


#### 2. 识别层 (Identification Layer)
is_target_pattern()        # 模式识别
contains_target_keywords() # 关键词匹配  
match_target_by_regex()    # 正则匹配

#### 3. 执行层 (Execution Layer)
execute_open_position()    # 开仓执行
execute_close_position()   # 平仓执行
check_close_positions()    # 平仓检查

#### 4. 风控层 (Risk Management)
meets_strategy_criteria()  # 策略条件验证
position_sizing()          # 仓位计算
risk_monitoring()          # 风险监控

### 文件结构
LhasaRetailHunter/
├── README.md                 # 项目说明
├── strategy_framework.py     # 策略框架代码
├── config_template.py        # 配置模板
├── examples/                 # 使用示例
│   ├── basic_usage.py       # 基础使用示例
│   └── custom_pattern.py    # 自定义模式示例
├── docs/                    # 文档
│   ├── implementation_guide.md    # 实现指南
│   └── theory_background.md       # 理论背景
└── tests/                   # 测试代码
    └── test_framework.py    # 框架测试

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能齐全的 Python 计算器
支持基本运算、高级运算、括号优先级、连续计算和历史记录
"""

import ast
import math
from typing import List


class SafeExpressionEvaluator:
    """
    安全的表达式求值器，使用 AST 解析防止安全漏洞
    只允许白名单内的操作：数字、运算符、函数调用
    """

    def __init__(self):
        self.math_module = math
        self.allowed_functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
        }
        self.allowed_names = {
            'pi': math.pi,
            'e': math.e,
        }

    def eval(self, expression: str) -> float:
        """
        安全地计算表达式
        只允许白名单内的操作
        """
        try:
            # 预处理：将 ^ 转换为 **
            expression = expression.replace('^', '**')
            # 解析 AST
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body)
        except ZeroDivisionError:
            raise ValueError("❌ 错误：除零错误")
        except (SyntaxError, TypeError):
            raise ValueError("❌ 错误：语法错误，请检查输入")
        except ValueError as e:
            if "math domain error" in str(e).lower():
                raise ValueError("❌ 错误：数学域错误（如负数开平方）")
            raise
        except Exception as e:
            raise ValueError(f"❌ 错误：{str(e)}")

    def _eval_node(self, node: ast.AST) -> float:
        """递归求值 AST 节点"""
        # 数字（整数或浮点数）
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            else:
                raise ValueError(f"不支持的常量类型：{type(node.value).__name__}")

        # 一元运算（如：-5）
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            else:
                raise ValueError(f"不支持的一元运算符：{type(node.op).__name__}")

        # 二元运算（如：2 + 3）
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            else:
                raise ValueError(f"不支持的二元运算符：{type(node.op).__name__}")

        # 函数调用（如：sqrt(16)）
        elif isinstance(node, ast.Call):
            # 获取函数名
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                # 处理 math.sqrt 这种形式
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'math':
                    # 如果用户输入了 math.sqrt，直接提取函数名
                    func_name = node.func.attr
                    if func_name not in self.allowed_functions:
                        raise ValueError(f"不支持的函数：{func_name}")
                else:
                    raise ValueError(f"不支持的属性访问：{node.func.attr}")
            else:
                raise ValueError("不支持的函数调用格式")

            # 检查函数是否允许
            if func_name not in self.allowed_functions:
                raise ValueError(f"不支持的函数：{func_name}")

            # 检查参数数量
            if len(node.args) != 1:
                raise ValueError(f"函数 {func_name} 需要1个参数")

            # 检查是否使用了关键字参数
            if node.keywords:
                raise ValueError(f"不支持关键字参数")

            # 计算参数
            arg = self._eval_node(node.args[0])

            # 调用函数
            return self.allowed_functions[func_name](arg)

        # 名称（如：pi, e）
        elif isinstance(node, ast.Name):
            if node.id in self.allowed_names:
                return float(self.allowed_names[node.id])
            else:
                raise ValueError(f"未定义的名称：{node.id}")

        else:
            raise ValueError(f"不支持的 AST 节点类型：{type(node).__name__}")


class Calculator:
    """计算器类，包含所有计算功能"""

    def __init__(self):
        """初始化计算器"""
        self.history: List[str] = []  # 存储计算历史
        self.welcome_shown = False  # 标记是否已显示欢迎信息
        self.evaluator = SafeExpressionEvaluator()  # 安全表达式求值器

    def show_welcome(self):
        """显示欢迎信息和操作指南"""
        if not self.welcome_shown:
            print("=" * 60)
            print("🔢 欢迎使用 Python 计算器 🔢")
            print("=" * 60)
            print("📋 支持的运算：")
            print("   • 基本运算：+, -, *, /, %, ** (幂运算)")
            print("   • 高级运算：sqrt() (开方), sin(), cos(), tan()")
            print("   • 对数函数：log() (自然对数), log10() (常用对数)")
            print("   • 括号：() 支持优先级计算")
            print("\n💡 使用示例：")
            print("   2 + 3 * 4")
            print("   sqrt(16) + sin(pi/2)")
            print("   log(100) / log(10)")
            print("\n📝 其他命令：")
            print("   history - 查看计算历史")
            print("   clear   - 清除历史记录")
            print("   quit/exit - 退出程序")
            print("=" * 60)
            self.welcome_shown = True

    def show_menu(self):
        """显示菜单"""
        print("\n" + "=" * 40)
        print("📊 计算历史记录：")
        if self.history:
            for i, record in enumerate(self.history[-10:], 1):  # 显示最近10条
                print(f"   {i}. {record}")
        else:
            print("   (暂无历史记录)")
        print("=" * 40)

    def get_user_input(self) -> str:
        """获取用户输入"""
        try:
            expression = input("\n🔸 请输入计算表达式 (输入 'quit' 退出): ").strip()
            return expression.lower()
        except KeyboardInterrupt:
            return "quit"

    def validate_expression(self, expression: str) -> bool:
        """验证表达式是否有效"""
        # 检查是否为空
        if not expression:
            print("❌ 错误：输入不能为空")
            return False

        # 检查是否是命令
        if expression.lower() in ['quit', 'exit', 'history', 'clear']:
            return True

        # 注意：不再需要字符白名单检查
        # AST 解析器会处理所有的安全检查和错误提示

        return True

    def calculate_basic(self, expression: str) -> float:
        """执行基本运算计算"""
        try:
            # 使用 AST 安全求值器（^ 转换在 eval 内部处理）
            result = self.evaluator.eval(expression)
            return result

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"❌ 错误：{str(e)}")

    def calculate_advanced(self, expression: str) -> float:
        """执行高级运算计算"""
        try:
            # 使用 AST 安全求值器（^ 转换在 eval 内部处理）
            result = self.evaluator.eval(expression)
            return result

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"❌ 错误：{str(e)}")

    def calculate(self, expression: str) -> float:
        """主计算函数，自动选择基本或高级运算"""
        # 检查是否包含高级函数
        advanced_functions = ['sqrt', 'sin', 'cos', 'tan', 'log', 'log10']
        if any(func in expression.lower() for func in advanced_functions):
            return self.calculate_advanced(expression)
        else:
            return self.calculate_basic(expression)

    def format_result(self, result: float) -> str:
        """格式化结果输出"""
        # 如果是整数，转换为整数显示
        if result.is_integer():
            return str(int(result))
        # 如果是接近整数的浮点数
        elif abs(result - round(result)) < 1e-10:
            return str(int(round(result)))
        # 否则保留适当的小数位数
        else:
            # 根据数值大小决定小数位数
            if abs(result) >= 1e6 or abs(result) <= 1e-4:
                return f"{result:.6e}"  # 科学计数法
            else:
                return f"{result:.8g}"  # 最多8位有效数字

    def add_to_history(self, expression: str, result: float):
        """添加计算记录到历史"""
        result_str = self.format_result(result)
        record = f"{expression} = {result_str}"
        self.history.append(record)

    def show_history(self):
        """显示完整历史记录"""
        if not self.history:
            print("\n📝 暂无历史记录")
            return

        print("\n" + "=" * 60)
        print("📊 完整计算历史记录")
        print("=" * 60)
        for i, record in enumerate(self.history, 1):
            print(f"{i:3d}. {record}")
        print("=" * 60)

    def clear_history(self):
        """清除历史记录"""
        self.history.clear()
        print("\n✅ 历史记录已清除")

    def run(self):
        """运行计算器主程序"""
        self.show_welcome()

        while True:
            try:
                # 显示菜单（每3次计算显示一次）
                if len(self.history) % 3 == 0:
                    self.show_menu()

                # 获取用户输入
                expression = self.get_user_input()

                # 处理退出命令
                if expression in ['quit', 'exit']:
                    print("\n👋 感谢使用计算器，再见！")
                    break

                # 处理特殊命令
                if expression == 'history':
                    self.show_history()
                    continue

                if expression == 'clear':
                    self.clear_history()
                    continue

                # 验证输入
                if not self.validate_expression(expression):
                    continue

                # 执行计算
                print("\n⏳ 正在计算...")
                result = self.calculate(expression)
                result_str = self.format_result(result)

                # 显示结果
                print(f"\n✅ 计算结果：{expression} = {result_str}")

                # 添加到历史
                self.add_to_history(expression, result)

            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见！")
                break
            except EOFError:
                print("\n\n👋 感谢使用计算器，再见！")
                break
            except ValueError as e:
                print(f"\n{e}")
                continue
            except Exception as e:
                print(f"\n❌ 发生未知错误：{str(e)}")
                continue


def main():
    """主函数"""
    calculator = Calculator()
    calculator.run()


if __name__ == "__main__":
    main()
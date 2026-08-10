"""
兼容模块 - 当 flasgger 不可用时提供替代实现
"""

try:
    from flasgger import swag_from
except ImportError:
    def swag_from(*args, **kwargs):
        """空装饰器 - 当 flasgger 不可用时使用"""
        def decorator(f):
            return f
        return decorator
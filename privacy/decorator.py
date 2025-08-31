def permission_required(permission_name: str):
    """
    一个简单的 RBAC 权限控制装饰器
    
    Args:
        permission_name (str): 所需的权限名称，例如 "model:upload"。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = None
            if 'request' in kwargs:
                request = kwargs['request']
            elif len(args) > 0 and isinstance(args[0], Request):
                request = args[0]
            
            if not request:
                raise RuntimeError("无法在装饰器中获取 Request 对象。请确保路由函数包含 Request 参数。")

            user = get_current_user(request) # 获取当前登录用户
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未授权: 请提供有效的用户凭证",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user_roles = get_user_roles(user.user_id)
            user_permissions = get_roles_permissions(user_roles) 
            if permission_name in user_permissions:
                return await func(*args, **kwargs) # 有权限，执行操作
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足: 您没有访问此资源的权限"
                )
        return wrapper
    return decorator


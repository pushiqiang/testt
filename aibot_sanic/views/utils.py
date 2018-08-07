from inspect import isawaitable

from marshmallow.exceptions import ValidationError
from sanic.exceptions import InvalidUsage
from sanic.response import json
from sanic.views import HTTPMethodView

from app import app
from views.exceptions import APIException, InvalidJSON, WrongRequestFormat


def ok_response(body, message="", *args, **kwargs):
    """成功的 response
    """
    new_body = {'ok': True, 'message': message, 'result': body}
    return json(new_body, *args, **kwargs)


def failed_response(error_type, error_message, *args, **kwargs):
    """失败的 response
    """
    body = {'ok': False, 'error_type': error_type, 'message': error_message}
    return json(body, *args, **kwargs)


def validation_error_response(validation_error, *args, **kwargs):
    """字段验证失败的 response
    validation_error: ValidationError
    """
    errors = list()
    for field in validation_error.field_names:
        field_error = {
            'error_type': 'validation_error',
            'field': field,
            'message': validation_error.messages[field][0]
        }
        errors.append(field_error)

    new_body = {'ok': False, 'errors': errors}
    return json(new_body, *args, **kwargs)


class APIBaseView(HTTPMethodView):
    """扩展 class based view, 增加异常处理
    """

    def parse_json(self, request, many=False):
        """解析 request body 为 json
        如果 many 为 True, 使请求数据为列表
        """
        try:
            parsed_data = request.json
        except InvalidUsage:
            raise InvalidJSON

        target_type = list if many else dict
        if not isinstance(parsed_data, target_type):
            raise WrongRequestFormat
        return parsed_data

    async def dispatch_request(self, request, *args, **kwargs):
        """扩展 http 请求的分发, 添加错误处理
        """
        try:
            response = super(APIBaseView, self).dispatch_request(
                request, *args, **kwargs)
            if isawaitable(response):
                response = await response
        except Exception as exception:
            response = await self.handle_exception(exception)
        return response

    async def handle_exception(self, exception):
        """处理异常
        ValidationError, APIException: 返回适当的错误信息
        else: 重新抛出异常
        """
        if isinstance(exception, ValidationError):
            response = validation_error_response(exception)
        elif isinstance(exception, APIException):
            response = failed_response(
                error_type=exception.error_type,
                error_message=exception.error_message)
        else:
            # 非 debug 模式下, 发送错误消息到 sentry
            if not app.config.DEBUG:
                app.sentry.captureException()
            raise exception
        return response


# 加入 GetView 和 UpdateView
class CreateView(APIBaseView):
    """创建数据的 view
    1. 获取上下文: 通过数据库或其他 model 层获取数据
    2. 验证请求数据
    3. 保存数据
    """
    serializer_class = None

    def get_serializer_class(self):
        """如果需要根据请求数据使用不同的 serializer, 在子类中覆盖这个方法
        """
        assert self.serializer_class is not None, \
            'Must assign serializer class'
        return self.serializer_class

    async def post(self, request, *args, **kwargs):
        self.context = await self.get_context(request, kwargs)

        serializer_class = self.get_serializer_class()
        # 反序列化请求数据
        serializer = serializer_class(strict=True, context=self.context)
        request_data = self.parse_json(request)
        self.validated_data, errors = serializer.load(request_data)

        # 保存数据
        await self.save()
        return self.response()

    async def get_context(self, request, kwargs):
        """从数据库获取上下文, 用于传入 serializer 中, 帮助验证请求数据
        默认返回空字典, 需要特定的上下文在子类中覆盖这个方法
        """
        return {}

    async def save(self):
        """根据 self.validated_data 和 self.context 保存数据到数据库
        """
        raise NotImplementedError

    def response(self):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        return ok_response({})

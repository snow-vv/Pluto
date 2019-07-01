# -*- coding: UTF-8 -*-
from django.http.response import HttpResponseBase, JsonResponse
from django.views import View

from common.exception import MedivhExceptionBase, LoginRequireException, PermissionDeniedException
from common.logger import log_error
from permission.utils import check_permission


class JsonView(View):
    login_require = True
    superuser_require = False
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                if self.login_require:
                    raise LoginRequireException
            else:
                if not request.user.is_superuser:
                    check_permission(
                        user=request.user,
                        permissions=self.permissions
                    )
            if self.superuser_require and not request.user.is_superuser:
                raise PermissionDeniedException

            response = super(JsonView, self).dispatch(request=request, **kwargs)

            if isinstance(response, HttpResponseBase):
                return response
            else:
                response = {'error': 0, 'message': '', 'data': response}
        except MedivhExceptionBase as e:
            response = {
                'error': e.code,
                'message': e.message,
            }
        except Exception as e:
            log_error()
            response = {
                'error': 500,
                'message': repr(e),
            }

        return JsonResponse(response)

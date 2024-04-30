from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    def successResponse(self, data, message, status, meta=None):
        response = {
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
            "meta": meta or {},
        }
        return Response(response, status=status)

    def errorResponse(self, errors, message, status):
        response = {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        }
        return Response(response, status=status)

    def someThingWentWrong(self):
        response = {
            "success": True,
            "message": "Something Went Wrong!",
            "data": None,
            "errors": None,
        }
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.http import JsonResponse


def health_check(request):
    """
    A simple health check view that returns a JSON response indicating the service is up and running.
    """
    return JsonResponse({"status": "ok", "message": "Service is up and running."})

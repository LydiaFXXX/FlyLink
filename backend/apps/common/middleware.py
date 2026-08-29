# Middleware to trust Cloudflare quick-tunnel origins for CSRF (demo / portable cloud mode)
class TrustCloudflareTunnelCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        if host.endswith('.trycloudflare.com') or host.endswith('.cfargotunnel.com'):
            origin = f"{'https' if request.is_secure() or request.META.get('HTTP_X_FORWARDED_PROTO') == 'https' else 'http'}://{request.get_host()}"
            # Mark as trusted dynamically for this request
            from django.conf import settings
            if origin not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(origin)
        return self.get_response(request)

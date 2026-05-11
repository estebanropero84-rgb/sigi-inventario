from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import re

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Agrega headers de seguridad adicionales"""
    
    def process_response(self, request, response):
        # Prevenir MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevenir XSS
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Control de referer
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (opcional)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class IpLoggerMiddleware(MiddlewareMixin):
    """Registra la IP del usuario en cada request"""
    
    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        request.client_ip = ip
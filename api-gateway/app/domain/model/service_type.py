from enum import Enum
import os

class ServiceType(str, Enum):
    AUTH = "auth"
    BLOG = "blog"

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
BLOG_SERVICE_URL = os.getenv("BLOG_SERVICE_URL")

SERVICE_URLS = {
    ServiceType.AUTH: AUTH_SERVICE_URL,
    ServiceType.BLOG: BLOG_SERVICE_URL,
}
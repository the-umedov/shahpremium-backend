"""Xavfsizlik audit hodisalari nomlari (audit_logs.action)."""


class SecurityEvent:
    LOGIN = "security.login"
    LOGIN_FAILED = "security.login_failed"
    LOGOUT = "security.logout"
    LOGOUT_ALL = "security.logout_all"
    PASSWORD_CHANGE = "security.password_change"
    PASSWORD_RESET_REQUEST = "security.password_reset_request"
    PASSWORD_RESET = "security.password_reset"
    EMAIL_CHANGE = "security.email_change"
    PHONE_CHANGE = "security.phone_change"
    CONTACT_VERIFIED = "security.contact_verified"
    PERMISSION_CHANGE = "security.permission_change"
    TWO_FACTOR_ENABLED = "security.2fa_enabled"
    TWO_FACTOR_DISABLED = "security.2fa_disabled"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    ACCOUNT_LOCKED = "security.account_locked"


NOTIFY_USER_EVENTS = {
    SecurityEvent.LOGIN,
    SecurityEvent.PASSWORD_CHANGE,
    SecurityEvent.PASSWORD_RESET,
    SecurityEvent.EMAIL_CHANGE,
    SecurityEvent.PHONE_CHANGE,
    SecurityEvent.TWO_FACTOR_ENABLED,
    SecurityEvent.TWO_FACTOR_DISABLED,
    SecurityEvent.SUSPICIOUS_ACTIVITY,
    SecurityEvent.ACCOUNT_LOCKED,
}

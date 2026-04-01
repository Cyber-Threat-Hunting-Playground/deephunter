from django.db import models
from django.utils import timezone

class Module(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class ModulePermission(models.Model):
    """
    Permissions associated with modules.
    IMPORTANT: this table does not store groups permissions, but only lists permissions used in DeepHunter.
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    permission = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.module.name}:{self.action}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['module', 'action'], name='unique_module_action')
        ]
        ordering = ['module__name', 'action']

class ApiKey(models.Model):
    KEY_TYPES = [
        ('READ', 'Read Only'),
        ('WRITE', 'Read and Write'),
    ]
    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=64, unique=True, editable=False)
    key_type = models.CharField(max_length=10, choices=KEY_TYPES, default='READ')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave empty for a key that never expires.")

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.name} ({self.key_type})"
    
    class Meta:
        ordering = ['-created_at']

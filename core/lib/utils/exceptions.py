# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Шмэлька | @hairpin01

# author: @Hairpin00
# version: 1.0.1
# description: Custom exceptions for kernel


class CommandConflictError(Exception):
    """Исключение для конфликта команд"""

    def __init__(self, message, conflict_type=None, command=None):
        super().__init__(message)
        self.conflict_type = conflict_type
        self.command = command


class McubTelethonError(Exception):
    pass


class CallInsecure(Exception):
    """Raised when a module attempts to access protected core internals."""

    def __init__(self, name: str, module_name: str | None = None):
        target = f"'{name}'"
        if module_name:
            message = f"Module '{module_name}' attempted insecure access to {target}"
        else:
            message = f"Insecure access to protected core attribute {target}"
        super().__init__(message)
        self.name = name
        self.module_name = module_name

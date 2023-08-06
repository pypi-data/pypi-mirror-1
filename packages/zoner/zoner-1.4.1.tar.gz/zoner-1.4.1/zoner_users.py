#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User management script for the Zoner TurboGears project.

This script is only needed during development for running from the project
directory. When the project is installed, easy_install will create a
proper zoner_users script.
"""

import sys
from zoner.commands import user_manage, ConfigurationError

if __name__ == "__main__":
    try:
        user_manage()
    except ConfigurationError, exc:
        sys.stderr.write(str(exc))
        sys.exit(1)

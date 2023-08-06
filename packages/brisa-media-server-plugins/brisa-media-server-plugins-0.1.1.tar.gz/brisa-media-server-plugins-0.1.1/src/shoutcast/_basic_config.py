# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os

from brisa.core import config


plugin = 'media_server_plugin-shoutcast'
user_home = os.path.expanduser('~')


def setup_basic_configuration():
    config.manager.set_parameter(plugin, 'owner', plugin)
    config.manager.set_parameter(plugin, 'enable', 'True')
    config.manager.set_parameter(plugin, 'show_mirrors', 'no')
    config.manager.set_parameter(plugin, 'preload', 'no')
    config.manager.set_parameter(plugin, 'ports', '80:443:8080')


def setup_fields_spec():
    config.manager.set_parameter(plugin, 'enable.field_type', 'checkbox')
    config.manager.set_parameter(plugin, 'enable.priority', '0')

    config.manager.set_parameter(plugin, 'show_mirrors.field_type', 'checkbox')
    config.manager.set_parameter(plugin, 'show_mirrors.priority', '1')

    config.manager.set_parameter(plugin, 'preload.field_type', 'checkbox')
    config.manager.set_parameter(plugin, 'preload.priority', '2')

    config.manager.set_parameter(plugin, 'ports.field_type', 'entry')
    config.manager.set_parameter(plugin, 'ports.priority', '3')


def main():
    setup_basic_configuration()
    setup_fields_spec()
    config.manager.save()


if __name__ == "__main__":
    main()

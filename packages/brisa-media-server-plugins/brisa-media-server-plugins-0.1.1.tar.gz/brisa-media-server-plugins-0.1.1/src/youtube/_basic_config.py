# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

import os

from brisa.core import config


plugin = 'media_server_plugin-youtube'
user_home = os.path.expanduser('~')


def setup_basic_configuration():
    config.manager.set_parameter(plugin, 'owner', plugin)
    config.manager.set_parameter(plugin, 'enable', 'True')
    config.manager.set_parameter(plugin, 'username', 'youtube_user')
    config.manager.set_parameter(plugin, 'video_url',
                                 'http://www.youtube.com/watch?v=')


def setup_fields_spec():
    config.manager.set_parameter(plugin, 'enable.field_type', 'checkbox')
    config.manager.set_parameter(plugin, 'enable.priority', '0')

    config.manager.set_parameter(plugin, 'username.field_type', 'entry')
    config.manager.set_parameter(plugin, 'username.priority', '1')

    config.manager.set_parameter(plugin, 'video_url.field_type', 'entry')
    config.manager.set_parameter(plugin, 'video_url.priority', '2')
    config.manager.set_parameter(plugin, 'video_url.field_label',
                                 'Base video URL')


def main():
    setup_basic_configuration()
    setup_fields_spec()
    config.manager.save()


if __name__ == "__main__":
    main()

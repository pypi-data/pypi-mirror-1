# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

from brisa.core import config


plugin_section = 'media_server_plugin-flickr'


def setup_basic_configuration():
    config.manager.set_parameter(plugin_section, 'owner', plugin_section)
    config.manager.set_parameter(plugin_section, 'enable', 'True')
    config.manager.set_parameter(plugin_section, 'username', 'flickr_user')
    config.manager.set_parameter(plugin_section, 'private', 'no')


def setup_fields_spec():
    config.manager.set_parameter(plugin_section, 'enable.field_type',
                                 'checkbox')
    config.manager.set_parameter(plugin_section, 'enable.priority',
                                 '0')

    config.manager.set_parameter(plugin_section, 'username.field_type',
                                 'entry')
    config.manager.set_parameter(plugin_section, 'username.priority',
                                 '2')

    config.manager.set_parameter(plugin_section, 'private.field_type',
                                 'checkbox')
    config.manager.set_parameter(plugin_section, 'private.priority',
                                 '1')
    config.manager.set_parameter(plugin_section, 'private.field_label',
                                 'Disable sharing of private photos')


def main():
    setup_basic_configuration()
    setup_fields_spec()
    config.manager.save()


if __name__ == '__main__':
    main()

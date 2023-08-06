# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

from brisa.core import config


class FieldSpec(object):

    def __init__(self, name, type, priority, label, initial_value):
        self.name = name
        self.type = type
        self.priority = priority
        self.label = label
        self.initial_value = initial_value

    def __cmp__(self, other):
        if self.priority == -1 and other.priority == -1:
            return 0

        if self.priority == -1:
            return 1

        if other.priority == -1:
            return -1

        return cmp(self.priority, other.priority)

    def __str__(self):
        return ' '.join(l.capitalize() for l in\
               self.name.replace('_', ' ').split(' '))


class Controller(object):

    def __init__(self):
        self.manager = config.manager

    def set_direct_access(self, access):
        """ Adjusts the model to perform operations directly on the database.
        """
        self.manager.set_direct_access(access)

    def set_parameter(self, section, parameter, value):
        """ Sets a parameter value in the given section.
        """
        self.manager.set_parameter(section, parameter, value)

    def get_parameter(self, section, parameter):
        """ Retrieves the value of a parameter in the given section.
        """
        return self.manager.get_parameter(section, parameter)

    def get_parameter_bool(self, section, parameter):
        """ Retrieves the value of a parameter which type is known to be a
        boolean (True or False). If the value is among 'yes', 'True', '1'
        or 'on', it will be evaluated as True.
        """
        return self.manager.get_parameter_bool(section, parameter)

    def get_parameter_list(self, section, parameter, token):
        """ Retrieves the value of a paramater and splits it by the token.
        """
        return self.manager.get_parameter_list(section, parameter, token)

    def get_field_spec(self, section, parameter):
        """ Returns a 4-tuple in the form (priority, field_type, field_label,
        initial_value).
        """
        priority = self.manager.get_parameter(section,
                                              '%s.priority' % parameter)
        field_type = self.manager.get_parameter(section,
                                                '%s.field_type' % parameter)
        field_label = self.manager.get_parameter(section,
                                                '%s.field_label' % parameter)

        if field_type == 'checkbox':
            initial_value = self.manager.get_parameter_bool(section,
                                                            parameter)
        else:
            initial_value = self.manager.get_parameter(section, parameter)

        if priority == '':
            priority = -1

        return FieldSpec(parameter, field_type, int(priority), field_label,
                         initial_value)

    def get_fields_specs(self, section, order=True):
        """ Return the names of all fields (filters fields used only
        internally). The list is ordered by priority if order is True.
        """
        specs = [self.get_field_spec(section, p) for p in\
                 self.items(section).keys() if '.priority' not in p and \
                 '.field_label' not in p and '.field_type' not in p and \
                 'owner' not in p]

        if order:
            specs = sorted(specs)

        return specs

    def get_plugin_fields_specs(self, plugin_name):
        return self.get_fields_specs('media_server_plugin-%s' % plugin_name)

    def get_plugin_names(self):
        """ Retrieves names of media server plugins.
        """
        names = self.manager.get_section_names()
        return [n.replace('media_server_plugin-', '') for n in names \
                if 'media_server_plugin' in n]

    def items(self, section):
        """ Returns a dict with all parameters of the given section. Keys are
        parameter names and values are parameter values.
        """
        return self.manager.items(section)

    def save(self):
        """ Saves the model.
        """
        self.manager.save()

    def revert(self):
        """ Reverts the model to the persistent state.
        """
        self.manager.update()

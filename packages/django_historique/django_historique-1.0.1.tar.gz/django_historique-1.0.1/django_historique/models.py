#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.base import ModelBase
from django.db import connection, transaction
from copy import deepcopy
import datetime


def log_instance (i, prefix=""):
    "Pour debug, affichage d'un objet et de ses attributs"
    print prefix, i, i.__class__.__name__
    for f in i._meta.fields:
        print prefix, "  ", f.name, f.__class__.__name__

class History (models.Model):
    "Classe abstraite de base pour l'historique"
    history_datetime = models.DateTimeField(default=datetime.datetime.now)
    history_objectid = models.PositiveIntegerField()
    history_revision = models.PositiveIntegerField()
    history_comment = models.CharField(max_length=1024, default="")

    def save_log (self, instance):
        "Enregistrement de l'instance courante avant l'ecriture de la nouvelle"
        if instance.id:
            iClass = instance.__class__
            hClass = self.__class__

            instance = iClass.objects.get(id = instance.id)
            self.history_objectid = instance.id
            self.history_comment = "pre_save history item <%s>" \
                    % (repr(instance))
            self.history_revision = hClass.objects.filter(history_objectid=instance.id).count()+1
    
            for field in instance._meta.fields:
                if field.__class__.__name__ != 'AutoField':
                    if getattr(field, 'unique', False):
                        field._unique = False
                    setattr(self, field.name, getattr(instance, field.name))

            #log_instance (instance, "I")
            #log_instance (self, "S")

            #self.save ()
            super (History, self).save ()

    def save (self):
        pass

    def diff_with (self, instance, ignore = None, \
            choice_value = True, verbose_names = True):
        ignored = ["history_datetime", "history_objectid", 
                "history_revision", "history_comment"]
        if ignore:
            ignored.extend (ignore)
        diffs = []
        for field in instance._meta.fields:
            if field.__class__.__name__ != 'AutoField' \
                    and field.name not in ignored:
                hvalue = getattr (self, field.name, "")
                if hvalue is None:
                    hvalue = ""
                ivalue = getattr (instance, field.name, "")
                if ivalue is None:
                    ivalue = ""
                if ivalue != hvalue:
                    if choice_value and len (field.choices) > 0:
                        for pair in field.choices:
                            if ivalue == pair[0]: ivalue = pair[1]
                            if hvalue == pair[0]: hvalue = pair[1]
                    
                    name = field.name
                    if verbose_names:
                        name = field.verbose_name

                    diffs.append({"name": name, \
                                  "previous": hvalue, \
                                  "updated": ivalue, \
                                  "date": getattr(self, 'history_datetime')})
        return diffs

    class Meta:
        abstract = True



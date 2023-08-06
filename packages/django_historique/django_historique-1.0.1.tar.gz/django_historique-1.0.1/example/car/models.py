from django.db import models
from django_historique import History
from django.db.models.signals import pre_save, pre_delete

class Brand (models.Model):
    name = models.CharField (max_length = 32)

    def __unicode__ (self):
        return "<Brand %s>" % self.name

class CarBase (models.Model):
    brand = models.ForeignKey (Brand)
    color = models.CharField (max_length = 32)

    class Meta:
        abstract = True

class CarHistory (History, CarBase):
    def __unicode__ (self):
        return "<CarH %s, rev. %s>" \
                % (self.history_objectid, self.history_revision)

class Car (CarBase):
    id = models.AutoField (primary_key = True)
    def __unicode__ (self):
        return "<Car %s>" % self.id

def carhistory_save (sender, instance, signal, *args, **kwargs):
    history = CarHistory ()
    history.save_log (instance)
pre_save.connect(carhistory_save, sender=Car)
pre_delete.connect(carhistory_save, sender=Car)

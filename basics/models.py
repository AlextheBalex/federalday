from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Document(models.Model):
    date = models.DateField(verbose_name=_("date of session"))
    legislative_period = models.IntegerField(verbose_name=_("legislative period"))
    document_id = models.IntegerField(verbose_name=_("document per period"))

    def __unicode__(self):
        return "%s/%s (%s)" % (self.legislative_period, self.document_id, self.date)

    def link_decorator(self):
        return reverse("basics:document", args=(self.document_id,))

class Party(models.Model):

    name = models.CharField(max_length=200, verbose_name=_("party name"), blank=True, default="")
    abbrev = models.CharField(max_length=200, verbose_name=_("abbreviation"))

    def __unicode__(self):
        return "%s" % self.abbrev


class Function(models.Model):

    name = models.CharField(max_length=200, verbose_name=_("function name"))

    def __unicode__(self):
        return "%s" % self.name


class RegularStatement(models.Model):

    text = models.TextField(verbose_name=_("text"))
    str_adjectives = models.TextField(verbose_name=_("standardized adjectives"), default=None)
    str_nouns = models.TextField(verbose_name=_("standardized nouns"), default=None)
    str_verbs = models.TextField(verbose_name=_("standardized verbs"), default=None)
    str_partizip_i = models.TextField(verbose_name=_("standardized partizip i"), default=None, null=True)
    str_other_words = models.TextField(verbose_name=_("other words"), default=None)
    str_persons = models.TextField(verbose_name=_("persons"), default=None)
    str_titles = models.TextField(verbose_name=_("wikipedia titles"), default=None)
    speaker = models.ForeignKey("basics.Speaker", verbose_name=_("who said it"))
    document = models.ForeignKey("basics.Document", verbose_name=_("source document"), default=None)
    order_id = models.IntegerField(verbose_name=_("order within document"), default=0)

    def __unicode__(self):
        return "%s-%s %s" % (self.document, self.order_id, self.speaker)

    def text_short_decorator(self):
        return self.text[:30]

    def str_nouns_short_decorator(self):
        return self.str_nouns[:30]

class Speaker(models.Model):

    name = models.CharField(max_length=200, verbose_name=_("speaker name"))
    party = models.ForeignKey("basics.Party", on_delete=models.CASCADE)
    function = models.ForeignKey("basics.Function", on_delete=models.CASCADE)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.party.abbrev)

    def link_decorator(self):
        return reverse("basics:speaker", args=(self.pk, ))

    def number_of_statements_decorator(self):
        return RegularStatement.objects.filter(speaker=self).count()
